# convert a serializer to a JSON Schema.
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

field_to_converter: ClassLookupDict = ClassLookupDict({})


def converter(converter_class):
    """Decorator to register a converter class"""
    if isinstance(converter_class.field_class, list):
        field_classes = converter_class.field_class
    else:
        field_classes = [converter_class.field_class]
    for field_class in field_classes:
        field_to_converter[field_class] = converter_class()
    return converter_class


def field_to_jsonschema(field):
    if isinstance(field, serializers.Serializer):
        result = to_jsonschema(field)
    else:
        converter = field_to_converter[field]
        result = converter.convert(field)
    if field.label:
        result["title"] = field.label
    if field.help_text:
        result["description"] = field.help_text
    # Add the default if it is set and ensure it is one of the native JSON types
    # so it can be serialized to JSON.
    if field.default and isinstance(field.default, (str, int, float, bool, list, dict)):
        result["default"] = field.default
    return result


def to_jsonschema(serializer):
    properties = {}
    required = []
    for name, field in serializer.fields.items():
        if field.read_only:
            continue
        sub_schema = field_to_jsonschema(field)
        if field.required:
            required.append(name)
        properties[name] = sub_schema

    result = {"type": "object", "properties": properties}
    if required:
        result["required"] = required
    return result
