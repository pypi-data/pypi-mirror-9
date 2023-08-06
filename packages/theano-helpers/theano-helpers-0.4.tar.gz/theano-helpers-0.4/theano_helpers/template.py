OPERATOR_TEMPLATE = '''
struct {% if name %}{{ name }}{% else %}Operator{% endif %} {
  {%- if description %}
  /****************************************************************************
   * {{ description }}
   ***************************************************************************/

  {% endif -%}
  {% for node, typedef in typenames.typedefs.iteritems() -%}
  typedef {{ typedef }} {{ typenames.names_by_node[node] }}_t;
  {% endfor %}
  {% for node, typedef in typenames.typedefs.iteritems() -%}
  {{ typenames.names_by_node[node] }}_t {{ typenames.names_by_node[node] }};
  {% endfor %}
  {% if name %}{{ name }}{% else %}Operator{% endif -%}
  ({%- for n in graph_inputs -%}
           {{ typenames.typenames[n] }} {{ typenames.names_by_node[n] }}
           {%- if not loop.last %}, {% endif %}
           {% endfor -%})
    : {% for node in typenames.typedefs %}{{ typenames.values[node] }}
      {%- if not loop.last %}, {% endif %}
      {% endfor %}
  {}

  {% set last_out_node, last_typedef = typenames.typedefs.items()[-1] %}
  {% set last_out_name = typenames.names_by_node[last_out_node] %}
  typedef {{ last_out_name }}_t iterator;
  {% for n in graph_inputs -%}
  typedef {{ typenames.typenames[n] }} {{ typenames.names_by_node[n] }}_t;
  {% endfor %}

  iterator begin() { return {{ last_out_name }}; }
};
'''

FUNCTION_HEADER_TEMPLATE = '''
#ifndef ___{% if name %}{{ name.upper() }}{% else %}OPERATOR{% endif %}__HPP___
#define ___{% if name %}{{ name.upper() }}{% else %}OPERATOR{% endif %}__HPP___

#include <stdint.h>
#include <thrust/iterator/transform_iterator.h>
#include <thrust/iterator/constant_iterator.h>
#include <thrust/device_vector.h>
#include <thrust/copy.h>
#include <thrust/transform.h>
#include <thrust/functional.h>
#include <thrust/tuple.h>
#include "src/functional.hpp"
#include "src/unpack_args.hpp"

#ifndef float32_t
typedef float float32_t;
#endif
#ifndef float64_t
typedef double float64_t;
#endif

{{ body }}

#endif  // #ifndef ___{% if name %}{{ name.upper() }}{% else %}OPERATOR{% endif %}__HPP___
'''


CYTHON_HEADER_TEMPLATE = '''
#cython: embedsignature=True
cimport numpy as np
import numpy as np
from cythrust.thrust.copy cimport copy_n
from cythrust.thrust.iterator.zip_iterator cimport make_zip_iterator
from cythrust.thrust.tuple cimport make_tuple2

cdef extern from {{ header_file }} nogil:
    cdef cppclass {{ name }}:
        cppclass iterator:
            pass
        {% for n in graph_inputs -%}
        cppclass {{ typenames.names_by_node[n] }}_t:
            pass
        {% endfor %}
        iterator begin()
        {{ name }}(
            {% for n in graph_inputs -%}
            {{ typenames.names_by_node[n] }}_t
            {%- if not loop.last %}, {% endif %}
            {%- endfor %})
'''
