{% macro celsius_to_fahrenheit(column_name) %}
    ({{ column_name }} * 9.0 / 5.0 + 32)
{% endmacro %}
