typenames = TypeNames(dfg)
node = node_data['node'].loc[0]
typenames.update(node)
typenames.update(node)
typenames.typenames
node
node = node_data['node'].loc[1]
node
op, args = extract_op(node)
op
args
#args
op, args, output = node.owner.op, node.owner.inputs, node.owner.outputs[0]
op
args[0]
typename(args[0])
typenames[args[0]]
'Transform2<thrust::multiplies<%s_t>, %s>' % (output.dtype, typenames[args[0]])
'Transform2<thrust::multiplies<%s_t>, %s>' % (output.dtype, ', '.join([typenames[arg] for arg in args]))
'Transform2<thrust::multiplies<%s_t>, %s>' % (output.dtype, ', '.join([typenames[arg] for arg in args]))
'Transform2<thrust::multiplies<%s_t>, %s >' % (output.dtype, ', '.join([typenames[arg] for arg in args]))
'Transform2<thrust::multiplies<%s_t>, %s >' % (output.dtype, ', '.join([typenames[arg] for arg in args]))
'Transform2<thrust::multiplies<%s_t>, %s >' % (output.dtype, ', '.join([typenames[arg] for arg in args]))
'Transform2<thrust::multiplies<%s_t>, %s >' % (output.dtype, ', '.join([typenames[arg] for arg in args]))
'Transform2<thrust::multiplies<%s_t>, %s >' % (output.dtype, ', '.join([typenames[arg] for arg in args]))
node_data
node_data['op'] = [n.owner.op for n in node_data['node']]
node_data['op']
node_data
node_data['inputs'] = [n.owner.inputs for n in node_data['node']]
node_data['output'] = [n.owner.outputs[0] for n in node_data['node']]
node_data
node_data['output_type'] = None
node_data
node_data.drop('output_type')
node_data.drop('output_type', axis=1)
node_data.drop('output_type', axis=1, inplace=True)
node_data['typedef'] = None
node_data
node_data.set_index('node')
node_data
typenames.update(node_data['node'].loc[0])
node_data['typedef'].loc[0] = typenames.update(node_data['node'].loc[0])
node_data.loc[0, 'typedef'] = typenames.update(node_data['node'].loc[0])
node_data
#print 'void operator() (%s) {' % ', '.join(['%s_t %s' % (typename(i), i.name) for i in inputs])
#'Transform2<thrust::multiplies<%s_t>, %s >' % (output.dtype, ', '.join([typenames[arg] for arg in args]))
#print 'void operator() (%s) {' % ', '.join(['%s_t %s' % (typename(i), i.name) for i in inputs])
a
~a
~a
-a
3 * (-a)
(3 * (-a)).owner.outputs[0]
(3 * (-a)).owner.outputs[0].type
#(3 * (-a)).owner.outputs[0].type
#(3 * (-a)).owner.op
(3 * (-a)).owner.op
(3 * (-a)).owner.inputs
node_data
typenames
typenames.typenames
typenames.update(node_data['node'].loc[1])
node_data
node_data.loc[0, 'input_dtypes'] = [typenames[i] for i in node_data.loc[0, 'inputs']]
node_data
node_data.loc[0, 'input_dtypes'] = [typenames[i] for i in node_data.loc[0, 'inputs']]
node_dat
node_dats
node_data
node = node_data['node'].loc[1]
node
node.owner.inputs
node_data.loc[1, 'input_dtypes'] = [typenames[i] for i in node_data.loc[1, 'inputs']]
node_data.loc[1, 'input_dtypes'].values[0] = [typenames[i] for i in node_data.loc[1, 'inputs']]
node_data.loc[1, 'input_dtypes']
node_data.iloc[1, 'input_dtypes']
node_data.iloc[1]
node_data.iloc[1, 'input_dtypes']
node_data.loc[1, 'input_dtypes']
node_data
node_data['input_dtypes'] = None
node_data.loc[0, 'input_dtypes'] = [typenames[i] for i in node_data.loc[0, 'inputs']]
node_data.loc[1, 'input_dtypes'] = [typenames[i] for i in node_data.loc[1, 'inputs']]
node_data
node_data.loc[1, 'input_dtypes']
node_data.loc[1, 'input_dtypes'] = [[typenames[i] for i in node_data.loc[1, 'inputs']]]
node_data[1, 'input_dtypes'] = [typenames[i] for i in node_data.loc[1, 'inputs']]
node_data[1, 'input_dtypes']
node_data.loc[1, 'input_dtypes']
node_data[1, 'input_dtypes'].values[0] = [typenames[i] for i in node_data.loc[1, 'inputs']]
node_data.loc[1, 'input_dtypes'].values[0] = [typenames[i] for i in node_data.loc[1, 'inputs']]
node_data.loc[1, 'input_dtypes'][0] = [typenames[i] for i in node_data.loc[1, 'inputs']]
node_data.loc[1, 'input_dtypes'] = [typenames[i] for i in node_data.loc[1, 'inputs']]
node_data.loc[1, 'input_dtypes'] = tuple(typenames[i] for i in node_data.loc[1, 'inputs']])
node_data.loc[1, 'input_dtypes'] = tuple(typenames[i] for i in node_data.loc[1, 'inputs'])
#node_data.loc[1, 'input_dtypes'] = tuple(typenames[i] for i in node_data.loc[1, 'inputs'])
node_data
node_data['input_dtypes'] = []
node_data['input_dtypes'] = [] * node_data.shape[0]
node_data['input_dtypes'] = [] * node_data.shape[0]
node_data['input_dtypes']
node_data['input_dtypes'] = [] * node_data.index.shape[0]
node_data['input_dtypes'] = [None] * node_data.index.shape[0]
node_data
node_data['input_dtypes'] = [[None]] * node_data.index.shape[0]
node_data
node_data['input_dtypes'] = [[]] * node_data.index.shape[0]
node_data
node_data.loc[0, 'input_dtypes'] = [typenames[i] for i in node_data.loc[0, 'inputs']]
node_data
#node_data.loc[0, 'input_dtypes'] = [typenames[i] for i in node_data.loc[0, 'inputs']]
node_data.loc[1, 'input_dtypes'] = [typenames[i] for i in node_data.loc[1, 'inputs']]
node_data.loc[1, 'input_dtypes'].extend([typenames[i] for i in node_data.loc[1, 'inputs']])
node_data
node_data.loc[1, 'input_dtypes']
node_data.loc[2, 'input_dtypes']
node_data.loc[2, 'input_dtypes']
#node_data.loc[2, 'input_dtypes']
node_data.drop('input_dtypes', axis=1, inplace=True)
node_data
node_data['inputs']
for k, v in node_data['inputs']:
	print k, v
for k, v in node_data['inputs'].iteritems():
	print k, v
[n.name if n.name else 'input%d_%d' % (k, i) for k, v in node_data['inputs'].iteritems() for i, n in enumerate(v)]
[[n.name if n.name else 'input%d_%d' % (k, i) for k, v in node_data['inputs'].iteritems()] for i, n in enumerate(v)]
[[n.name if n.name else 'input%d_%d' % (k, i) for i, n in enumerate(v)] for k, v in node_data['inputs'].iteritems()]
