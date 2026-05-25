{% test jsonb_dims_length(model, column_name, expected_length=1024) -%}
select *
from {{ model }}
where {{ column_name }} is null
   or jsonb_typeof({{ column_name }}->'dims') is distinct from 'array'
   or jsonb_array_length({{ column_name }}->'dims') != {{ expected_length }}
{% endtest %}
