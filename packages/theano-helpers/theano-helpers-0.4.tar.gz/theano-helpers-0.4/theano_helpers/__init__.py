import pprint
import cStringIO as StringIO
import itertools
from collections import OrderedDict

import theano
import theano.tensor as T
import nested_structures
import pandas as pd
import jinja2
from .template import (OPERATOR_TEMPLATE, FUNCTION_HEADER_TEMPLATE,
                       CYTHON_HEADER_TEMPLATE)


CTYPE_BY_THEANO_TYPE = OrderedDict([('uint8', 'uint8_t'),
                                    ('uint16', 'uint16_t'),
                                    ('uint32', 'uint32_t'),
                                    ('uint64', 'uint64_t'),
                                    ('int8', 'int8_t'),
                                    ('int16', 'int16_t'),
                                    ('int32', 'int32_t'),
                                    ('int64', 'int64_t'),
                                    ('float32', 'float'),
                                    ('float64', 'double')])


def what_am_i(node):
    if node.owner:
        node, args = extract_op(node)
    if isinstance(node, theano.scalar.basic.Mul):
        return 'multiply'
    elif isinstance(node, theano.scalar.basic.IntDiv):
        return 'divide_floor'
    elif isinstance(node, theano.scalar.basic.TrueDiv):
        return 'divide'
    elif isinstance(node, theano.scalar.basic.Add):
        return 'add'
    elif isinstance(node, theano.scalar.basic.Sub):
        return 'subtract'
    elif isinstance(node, theano.tensor.elemwise.DimShuffle):
        return 'broadcast'
    elif isinstance(node, theano.scalar.basic.Pow):
        return 'pow'
    elif isinstance(node, theano.scalar.basic.Sqr):
        return 'sqr'
    elif isinstance(node, theano.scalar.basic.Sqrt):
        return 'sqrt'
    elif isinstance(node, theano.tensor.TensorConstant):
        return node.value
    elif isinstance(node, theano.tensor.TensorVariable):
        return node.name


operation = lambda v: v.owner.op.scalar_op if hasattr(v.owner.op, 'scalar_op') else v.owner.op
arguments = lambda v: v.owner.inputs
extract_op = lambda t: (operation(t), arguments(t)) if t.owner else t
extract_node = lambda t: (t, arguments(t)) if t.owner else t

# TODO:
#
#  - Implement support for indirect vector element access
#   * See [`TensorVariable.take`][1] and [`thrust::permutation_iterator`][2].
#
# [1]: http://deeplearning.net/software/theano/library/tensor/basic.html#tensor._tensor_py_operators.take
# [2]: https://thrust.github.io/doc/classthrust_1_1permutation__iterator.html
def extract(node):
    try:
        #op, args = extract_op(node)
        node, args = extract_node(node)
        op, op_args = extract_op(node)
        if isinstance(op, theano.tensor.basic.Flatten):
            return extract(args[0])
        elif args is None:
            return node
        else:
            return (node, map(extract, args))
    except (ValueError, TypeError):
        # `node` is a leaf node, *not* an operation.
        return node


class DataFlowGraph(object):
    def __init__(self, operation_graph):
        self.operation_graph = operation_graph
        self.tree = nested_structures.apply_depth_first(
            [extract(operation_graph)], lambda node, *args: node, as_dict=True)
        for n in self.flatten():
            try:
                node, args = extract_node(n)
                inputs = n.owner.inputs
                for k, i in enumerate(inputs):
                    op, op_args = extract_op(i)
                    if isinstance(op, theano.tensor.basic.Flatten):
                        n.owner.inputs[k] = i.owner.inputs[0]
            except (ValueError, TypeError):
                pass

    def collect(self, func=None):
        if func is None:
            func = lambda key, *args: key
        return nested_structures.dict_collect(self.tree, func)

    def flatten(self):
        return self.collect()

    def __str__(self):
        return pprint.pformat(map(what_am_i, self.flatten()))


class Expression(object):
    def __init__(self):
        self.output = StringIO.StringIO()

    def pre(self, v, node, parents, first, last):
        self.output.write('(%s)%s' % (v.type.dtype, what_am_i(v)))
        if node.children is not None:
            self.output.write('(')

    def post(self, v, node, parents, first, last):
        if node.children is not None:
            self.output.write(')')
        if not last:
            self.output.write(', ')


class TypeNames(object):
    def __init__(self, dfg):
        inputs = [n for n in dfg.flatten() if not n.owner]
        self.nodes_by_name = OrderedDict([(n.name, n)
                                          if n.name else
                                          ('iterator_%d' % i, n)
                                          for i, n in
                                          enumerate(dfg.flatten())])
        self.names_by_node = OrderedDict([(node, name)
                                          for name, node in
                                          self.nodes_by_name.iteritems()])
        self.typenames = OrderedDict()
        self.typedefs = OrderedDict()
        self.values = OrderedDict()
        self.handler = OrderedDict()
        for i in inputs:
            self.update(i)

    def __getitem__(self, node):
        return self.typenames[node]

    def __in__(self, node):
        return node in self.typenames

    def handle_scalar(self, node):
        op, (arg, ) = extract_op(node)
        self.typedefs[node] = ('thrust::constant_iterator<' +
                               self.typenames[arg] + ' >')
        name = self.names_by_node[node]
        if hasattr(arg, 'value'):
            value = arg.value
        else:
            value = arg.name
        self.values[node] = '%s(%s)' % (name, value)

    def handle_unary(self, node):
        THRUST_OP_BY_THEANO = OrderedDict([
            (theano.scalar.basic.Abs, 'cythrust::absolute'),
            #(theano.scalar.basic.Angle, 'cythrust::'),
            (theano.scalar.basic.ArcCos, 'cythrust::acos_'),
            #(theano.scalar.basic.ArcCosh, 'cythrust::acos_'),
            (theano.scalar.basic.ArcSin, 'cythrust::asin_'),
            #(theano.scalar.basic.ArcSinh, 'cythrust::'),
            (theano.scalar.basic.ArcTan, 'cythrust::atan_'),
            (theano.scalar.basic.ArcTan2, 'cythrust::atan2_'),
            #(theano.scalar.basic.ArcTanh, 'cythrust::'),
            ((theano.scalar.basic.Cast, theano.tensor.basic.Flatten),
             'thrust::identity'),
            (theano.scalar.basic.Ceil, 'cythrust::ceil_'),
            #(theano.scalar.basic.Clip, 'cythrust::'),
            (theano.scalar.basic.Cos, 'cythrust::cos_'),
            (theano.scalar.basic.Cosh, 'cythrust::cosh_'),
            #(theano.scalar.basic.Deg2Rad, 'cythrust::'),
            #(theano.scalar.basic.Exp, 'cythrust::'),  # $e^{a}$
            #(theano.scalar.basic.Exp2, 'cythrust::'),  # $2^{a}$
            #(theano.scalar.basic.Expm1, 'cythrust::'),  # $e^{a} - 1$
            (theano.scalar.basic.Floor, 'cythrust::floor_'),
            (theano.scalar.basic.Inv, 'cythrust::inv_'),  # $1 / a$
            (theano.scalar.basic.Invert, 'cythrust::logical_not'),  # $~a$
            #(theano.scalar.basic.Log, 'cythrust::'),  # Log base $e$
            #(theano.scalar.basic.Log10, 'cythrust::'),  # Log base 10
            #(theano.scalar.basic.Log1p, 'cythrust::'),  # $\ln(1 + a)$
            #(theano.scalar.basic.Log2, 'cythrust::'),  # Log base 2
            (theano.scalar.basic.Neg, 'cythrust::negate'),  # Negative
            #(theano.scalar.basic.Rad2Deg, 'cythrust::'),
            #(theano.scalar.basic.RoundHalfAwayFromZero, 'cythrust::'),
            #(theano.scalar.basic.RoundHalfToEven, 'cythrust::'),
            (theano.scalar.basic.Sgn, 'cythrust::sign'),  # Sign
            (theano.scalar.basic.Sin, 'cythrust::sin_'),
            (theano.scalar.basic.Sinh, 'cythrust::sinh_'),
            (theano.scalar.basic.Sqr, 'cythrust::square'),
            (theano.scalar.basic.Sqrt, 'cythrust::square_root'),
            (theano.scalar.basic.Tan, 'cythrust::tan_'),
            (theano.scalar.basic.Tanh, 'cythrust::tanh_'),
            (theano.scalar.basic.Trunc, 'cythrust::trunc_'),  # `(a >= 0) ? floor(a) : -floor(-a)`
        ])

        op_type = None
        op, (arg, ) = extract_op(node)

        for theano_class, thrust_type in THRUST_OP_BY_THEANO.iteritems():
            if isinstance(op, theano_class):
                op_type = ('%s<' % thrust_type +
                           CTYPE_BY_THEANO_TYPE[node.owner.out.dtype] + '>')

        if op_type is None:
            raise ValueError('Unhandled operator type: %s' % op)

        self.typedefs[node] = ('thrust::transform_iterator<%s, %s >' %
                               (op_type, self.typenames[arg]))
        name = self.names_by_node[node]
        self.typenames[node] = '%s_t' % name
        self.values[node] = ('%s(%s, %s())' % (name, self.names_by_node[arg],
                                               op_type))

    def handle_ternary(self, node):
        THRUST_OP_BY_THEANO = OrderedDict([
            (theano.scalar.basic.Switch, 'cythrust::switch_'), # `a ? b : c`
        ])

        op_type = None
        op, args = extract_op(node)

        if isinstance(op, theano.tensor.basic.ARange):
            start, stop, step = args
            # TODO: We should be able to support different step sizes by
            # wrapping the `counting_iterator` in a `transform_iterator` that
            # applies a `multiplies` functor to multiply by the step value.
            if step.value != 1:
                raise ValueError('Only ranges with step == 1 are currently '
                                 'supported.')
            self.typedefs[node] = ('thrust::counting_iterator<' +
                                   self.typenames[stop] + ' >')
            name = self.names_by_node[node]
            self.typenames[node] = '%s_t' % name
            self.values[node] = '%s(%s)' % (name, start.value)
            return

        for theano_class, thrust_type in THRUST_OP_BY_THEANO.iteritems():
            if isinstance(op, theano_class):
                op_type = ('%s<' % thrust_type +
                           CTYPE_BY_THEANO_TYPE[node.owner.out.dtype] + '>')

        if op_type is None:
            raise ValueError('Unhandled operator type: %s' % op)

        self.typedefs[node] = (
            'thrust::transform_iterator<unpack_ternary_args<' + op_type + ' >,'
            'thrust::zip_iterator<'
            'thrust::tuple<' + ', '.join([self.typenames[a] for a in args]) + ' > > >')

        name = self.names_by_node[node]
        self.typenames[node] = '%s_t' % name
        self.values[node] = ('%s(thrust::make_zip_iterator(thrust::make_tuple(%s)), unpack_ternary_args<%s >(%s()))'
                             % (name, ', '.join([self.names_by_node[a]
                                                 for a in args]), op_type,
                                op_type))

    def handle_binary(self, node):
        THRUST_OP_BY_THEANO = OrderedDict([
            (theano.scalar.basic.Add, 'thrust::plus'),
            (theano.scalar.basic.AND, 'thrust::bit_and'),
            (theano.scalar.basic.EQ, 'thrust::equal_to'),
            (theano.scalar.basic.GE, 'thrust::greater_equal'),
            (theano.scalar.basic.GT, 'thrust::greater'),
            (theano.scalar.basic.LE, 'thrust::less_equal'),
            (theano.scalar.basic.LT, 'thrust::less'),
            (theano.scalar.basic.Minimum, 'thrust::minimum'),
            (theano.scalar.basic.Maximum, 'thrust::maximum'),
            (theano.scalar.basic.Mod, 'thrust::modulus'),
            (theano.scalar.basic.Mul, 'thrust::multiplies'),
            (theano.scalar.basic.NEQ, 'thrust::not_equal_to'),
            (theano.scalar.basic.OR, 'thrust::bit_or'),
            (theano.scalar.basic.Pow, 'cythrust::power'),  # `pow(a, b)`, i.e., $a ^ b$
            (theano.scalar.basic.Sqrt, 'cythrust::square_root'),
            (theano.scalar.basic.Sub, 'thrust::minus'),
            ((theano.scalar.basic.TrueDiv, theano.scalar.basic.IntDiv),
             'thrust::divides'),
            (theano.scalar.basic.XOR, 'thrust::bit_xor'),
        ])

        op_type = None
        op, args = extract_op(node)

        if isinstance(op, theano.tensor.subtensor.AdvancedSubtensor1):
            self.typedefs[node] = ('thrust::permutation_iterator<' +
                                   ', '.join([self.typenames[a] for a in args])
                                   + ' >')
            name = self.names_by_node[node]
            self.typenames[node] = '%s_t' % name
            self.values[node] = '%s(%s)' % (name,
                                            ', '.join([self.names_by_node[a]
                                                       for a in args]))
            return

        for theano_class, thrust_type in THRUST_OP_BY_THEANO.iteritems():
            if isinstance(op, theano_class):
                op_type = ('%s<' % thrust_type +
                           CTYPE_BY_THEANO_TYPE[node.owner.out.dtype] + '>')

        if op_type is None:
            raise ValueError('Unhandled operator type: %s' % op)

        self.typedefs[node] = (
            'thrust::transform_iterator<unpack_binary_args<' + op_type + ' >,'
            'thrust::zip_iterator<'
            'thrust::tuple<' + ', '.join([self.typenames[a] for a in args]) + ' > > >')
        name = self.names_by_node[node]
        self.typenames[node] = '%s_t' % name
        self.values[node] = ('%s(thrust::make_zip_iterator(thrust::make_tuple(%s)), unpack_binary_args<%s >(%s()))'
                             % (name, ', '.join([self.names_by_node[a]
                                                 for a in args]), op_type,
                                op_type))

    def update(self, node):
        if node.owner:
            op, args = extract_op(node)
            if isinstance(op, theano.tensor.elemwise.DimShuffle):
                self.typenames[node] = ('thrust::constant_iterator<' +
                                        self.typenames[args[0]] + ' >')
                self.handle_scalar(node)
            elif len(args) == 3:
                self.handle_ternary(node)
            elif len(args) == 2:
                self.handle_binary(node)
            elif len(args) == 1:
                self.handle_unary(node)
            else:
                raise ValueError('Unhandled operator type: %s' % op)
        elif isinstance(node, theano.tensor.TensorConstant):
            self.values[node] = node.value
            self.typenames[node] = CTYPE_BY_THEANO_TYPE[node.dtype]
        elif isinstance(node, theano.tensor.TensorVariable):
            dtype = node.dtype + '_t'
            if node.type.ndim == 0:
                self.typenames[node] = dtype
            elif node.type.ndim == 1:
                self.typenames[node] = \
                    'typename thrust::device_vector<%s>::iterator' % dtype
        return self[node]


class ThrustCode(object):
    def __init__(self, dfg):
        self.dfg = dfg
        ordered_nodes = sorted([(depth, node)
                                for node, wrapper, parents, first, last, depth in
                                dfg.collect(lambda *args: args) if node.owner],
                            key=lambda x: -x[0])
        node_data = pd.DataFrame(ordered_nodes, columns=['height', 'node'])

        typenames = TypeNames(dfg)
        node_data['inputs'] = [n.owner.inputs for n in node_data['node']]
        node_data['output'] = [n.owner.out for n in node_data['node']]

        for n in node_data['output']:
            typenames.update(n)
        output_nodes = node_data['output'].drop_duplicates()

        graph_inputs = []
        for inputs in node_data['inputs']:
            for n in inputs:
                if getattr(n, 'name', None) and (
                        n not in itertools.chain(output_nodes, graph_inputs)):
                    graph_inputs.append(n)

        self.typenames = typenames
        self.output_nodes = output_nodes
        self.graph_inputs = graph_inputs
        self.node_data = node_data

    def iterator_code(self, name):
        iterator_template = jinja2.Template(OPERATOR_TEMPLATE)

        iterator_code = iterator_template.render(name=name,
                                                 typenames=self.typenames,
                                                 description=
                                                 'Equivalent code: `%s`' %
                                                 theano.pp(self.dfg
                                                           .operation_graph),
                                                 graph_inputs=
                                                 self.graph_inputs)
        return iterator_code

    def header_code(self, name):
        header_template = jinja2.Template(FUNCTION_HEADER_TEMPLATE)
        header_code = header_template.render(name=name,
                                             body=self.iterator_code(name))
        return header_code

    def cython_header_code(self, name, header_file):
        cython_header_template = jinja2.Template(CYTHON_HEADER_TEMPLATE)
        return cython_header_template.render(header_file=header_file,
                                             name=name,
                                             graph_inputs=self.graph_inputs,
                                             typenames=self.typenames)


if __name__ == '__main__':
    from path_helpers import path

    pd.set_option('display.width', 300)
    # Example usage
    scalar = T.iscalar('scalar')
    exp = T.scalar('exp', dtype='float32')
    a = T.vector('view1', dtype='uint8')
    b = T.vector('view2', dtype='int32')

    dfg = DataFlowGraph((scalar * a) / (b ** exp))
    thrust_code = ThrustCode(dfg)

    with path('~/local/include/test.hpp').expand().open('wb') as output:
        output.write(thrust_code.header_code('Foo'))


