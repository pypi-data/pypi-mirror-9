import calendar
from datetime import datetime
import re
import time

import aniso8601
from flask import url_for, current_app
import six
from werkzeug.utils import cached_property

from . import natural_keys
from .utils import get_value
from .reference import ResourceReference, ResourceBound
from .schema import Schema


class Raw(Schema):
    """
    :param io: one of "r", "w" or "rw" (default); used to control presence in fieldsets/parent schemas
    :param schema: JSON-schema for field, or :class:`callable` resolving to a JSON-schema when called
    :param default: optional default value, must be JSON-convertible
    :param attribute: key on parent object, optional.
    :param nullable: whether the field is nullable.
    :param title: optional title for JSON schema
    :param description: optional description for JSON schema
    """

    def __init__(self, schema, io="rw", default=None, attribute=None, nullable=False, title=None, description=None):
        self._schema = schema
        self.default = default
        self.attribute = attribute
        self.nullable = nullable
        self.title = title
        self.description = description
        self.io = io

    def _finalize_schema(self, schema, io):
        """
        :return: new schema updated for field `nullable`, `title`, `description` and `default` attributes.
        """
        schema = dict(schema)
        
        if self.io == "r" and "r" in io:
            schema["readOnly"] = True

        if "null" in schema.get("type", []):
            self.nullable = True
        elif self.nullable:
            if "anyOf" in schema:
                if not any("null" in choice.get("type", []) for choice in schema["anyOf"]):
                    schema["anyOf"].append({"type": "null"})
            elif "oneOf" in schema:
                if not any("null" in choice.get("type", []) for choice in schema["oneOf"]):
                    schema["oneOf"].append({"type": "null"})
            else:
                try:
                    type_ = schema["type"]
                    if isinstance(type_, (str, dict)):
                        schema["type"] = [type_, "null"]
                    else:
                        schema["type"].append("null")
                except KeyError:
                    if len(schema) == 1 and "$ref" in schema:
                        schema = {"anyOf": [schema, {"type": "null"}]}
                    else:
                        current_app.logger.warn('{} is nullable but "null" type cannot be added'.format(self))

        for attr in ("default", "title", "description"):
            value = getattr(self, attr)
            if value is not None:
                schema[attr] = value
        return schema

    def schema(self):
        """
        JSON schema representation
        """
        schema = self._schema
        if callable(schema):
            schema = schema()

        if isinstance(schema, Schema):
            read_schema, write_schema = schema.response, schema.request
        elif isinstance(schema, tuple):
            read_schema, write_schema = schema
        else:
            return self._finalize_schema(schema, "rw")

        return self._finalize_schema(read_schema, "r"), self._finalize_schema(write_schema, "w")

    def format(self, value):
        """
        Format a Python value representation for output in JSON. Noop by default.
        """
        if value is not None:
            return self.formatter(value)
        return value

    def convert(self, instance, validate=True):
        """
        Convert a JSON value representation to a Python object. Noop by default.
        """
        if validate:
            instance = super(Raw, self).convert(instance)

        if instance is not None:
            return self.converter(instance)
        return instance

    def formatter(self, value):
        return value

    def converter(self, value):
        return value

    def output(self, key, obj):
        key = key if self.attribute is None else self.attribute
        return self.format(get_value(key, obj, self.default))

    def __repr__(self):
        return '{}(attribute={})'.format(self.__class__.__name__, repr(self.attribute))


class Any(Raw):
    def __init__(self, **kwargs):
        super(Any, self).__init__({"type": ["null", "string", "number", "boolean", "object", "array"]}, **kwargs)

def _field_from_object(parent, cls_or_instance):
    # --- start of Flask-RESTful code ---
    # Copyright (c) 2013, Twilio, Inc.
    # All rights reserved.
    # This code is part of or substantially similar to code in Flask-RESTful and is governed by its
    # license. Please see the LICENSE file in the root of this package.
    if isinstance(cls_or_instance, type):
        container = cls_or_instance()
    else:
        container = cls_or_instance
    if not isinstance(container, Schema):
        raise RuntimeError('{} expected Raw or Schema, but got {}'.format(parent, container.__class__.__name__))
    if not isinstance(container, Raw):
        container = Raw(container)
    # --- end of Flask-RESTful code ---
    return container


class Custom(Raw):
    """
    Arbitrary schema field type with optional formatter/converter transformers.

    :param dict schema: JSON-schema
    :param callable converter: convert function
    :param callable formatter: format function
    """

    def __init__(self, schema, converter=None, formatter=None, **kwargs):
        super(Custom, self).__init__(schema, **kwargs)
        self._converter = converter
        self._formatter = formatter

    def format(self, value):
        if self._formatter is None:
            return value
        return self._formatter(value)

    def converter(self, value):
        if self._converter is None:
            return value
        return self._converter(value)


class Array(Raw):
    """
    A field for an array of a given field type.

    :param Raw cls_or_instance: field class or instance
    """

    def __init__(self, cls_or_instance, min_items=None, max_items=None, **kwargs):
        self.container = container = _field_from_object(self, cls_or_instance)

        schema_properties = [('type', 'array')]
        schema_properties += [(k, v) for k, v in [('minItems', min_items), ('maxItems', max_items)] if v is not None]
        schema = lambda s: dict([('items', s)] + schema_properties)

        super(Array, self).__init__(lambda: (schema(container.response), schema(container.request)), **kwargs)

    def formatter(self, value):
        return [self.container.format(v) for v in value]

    def converter(self, value):
        return [self.container.convert(v) for v in value]


List = Array


class Object(Raw):
    """
    A versatile field for an object, containing either properties all of a single type, properties matching a pattern,
    or named properties matching some fields.

    `Raw.attribute` is not used in pattern properties and additional properties.

    :param properties: field class, instance, or dictionary of {property: field} pairs
    :param str pattern: an optional regular expression that all property keys must match
    :param dict pattern_properties: dictionary of {property: field} pairs
    :param Raw additional_properties: field class or instance
    """

    def __init__(self, properties=None, pattern=None, pattern_properties=None, additional_properties=None, **kwargs):
        self.properties = None
        self.pattern_properties = None
        self.additional_properties = None

        if isinstance(properties, dict):
            self.properties = properties
        elif isinstance(properties, (type, Raw)):
            field = _field_from_object(self, properties)
            if pattern:
                self.pattern_properties = {pattern: field}
            else:
                self.additional_properties = field

        def schema():
            request = {"type": "object"}
            response = {"type": "object"}

            for schema, attr in ((request, "request"), (response, "response")):
                if self.properties:
                    schema["properties"] = {key: getattr(field, attr) for key, field in self.properties.items()}
                if self.pattern_properties:
                    schema["patternProperties"] = {pattern: getattr(field, attr)
                                                   for pattern, field in self.pattern_properties.items()}
                if self.additional_properties:
                    schema["additionalProperties"] = getattr(self.additional_properties, attr)
                else:
                    schema["additionalProperties"] = False

            return response, request

        if self.pattern_properties and (len(self.pattern_properties) > 1 or self.additional_properties):
            raise NotImplementedError("Only one pattern property is currently supported "
                                      "and it cannot be combined with additionalProperties")

        super(Object, self).__init__(schema, **kwargs)

    @cached_property
    def _property_attributes(self):
        return [field.attribute or key for key, field in self.properties.items()]

    def format(self, value):
        output = {}

        if self.properties:
            output = {key: field.format(get_value(field.attribute or key, value, field.default)) for key, field in self.properties.items()}
        else:
            output = {}

        if self.pattern_properties:
            pattern, field = next(iter(self.pattern_properties.items()))

            if not self.additional_properties:
                output.update({key: field.format(get_value(key, value, field.default))
                               for key, value in value.items() if key not in self._property_attributes})
            else:
                raise NotImplementedError()
                # TODO match regular expression
        elif self.additional_properties:
            field = self.additional_properties
            output.update({key: field.format(get_value(key, value, field.default))
                           for key, value in value.items() if key not in self._property_attributes})

        return output

    def converter(self, instance):
        result = {}

        if self.properties:
            result = {field.attribute or key: field.convert(instance.get(key, None)) for key, field in self.properties.items()}

        if self.pattern_properties:
            pattern, field = next(iter(self.pattern_properties.items()))

            if not self.additional_properties:
                result.update({key: field.convert(value)
                               for key, value in instance.items() if key not in result})
            else:
                raise NotImplementedError()
                # TODO match regular expression
        elif self.additional_properties:
            field = self.additional_properties
            result.update({key: field.convert(value) for key, value in instance.items() if key not in result})

        return result


class AttributeMapped(Object):
    """
    Maps property keys from a JSON object to a list of items using `mapping_attribute`. The mapping attribute is the
    name of the attribute where the value of the property key is set on the property values.

    .. seealso::

        :class:`InlineModel` field is typically used with this field in a common SQLAlchemy pattern.

    :param Raw cls_or_instance: field class or instance
    :param str pattern: an optional regular expression that all property keys must match
    :param str mapping_attribute: mapping attribute
    """

    def __init__(self, cls_or_instance, mapping_attribute=None, **kwargs):
        self.mapping_attribute = mapping_attribute
        # TODO reject additional_properties, properties, pattern_properties, pattern
        super(AttributeMapped, self).__init__(additional_properties=cls_or_instance, **kwargs)

    def _set_mapping_attribute(self, obj, value):
        setattr(obj, self.mapping_attribute, value)
        return obj

    def format(self, value):
        return {get_value(self.mapping_attribute, v, None): self.additional_properties.format(v) for v in value}

    def converter(self, value):
        return [self._set_mapping_attribute(self.additional_properties.convert(v), k) for k, v in value.items()]


class String(Raw):
    """
    :param int min_length: minimum length of string
    :param int max_length: maximum length of string
    :param str pattern: regex pattern that the string must match
    :param list enum: list of strings with enumeration
    """

    def __init__(self, min_length=None, max_length=None, pattern=None, enum=None, format=None, **kwargs):
        schema = {"type": "string"}

        for v, k in ((min_length, 'minLength'),
                     (max_length, 'maxLength'),
                     (pattern, 'pattern'),
                     (enum, 'enum'),
                     (format, 'format')):
            if v is not None:
                schema[k] = v

        super(String, self).__init__(schema, **kwargs)

try:
    from datetime import timezone
except ImportError:
    from datetime import tzinfo, timedelta

    class timezone(tzinfo):
        def __init__(self, utcoffset, name=None):
            self._utcoffset = utcoffset
            self._name = name

        def utcoffset(self, dt):
            return self._utcoffset

        def tzname(self, dt):
            return self._name

        def dst(self, dt):
            return timedelta(0)

    timezone.utc = timezone(timedelta(0), 'UTC')


class Date(Raw):
    """
    A field for EJSON-style date-times in the format ``{"$date": MILLISECONDS_SINCE_EPOCH}``
    """

    def __init__(self, **kwargs):
        # TODO is a 'format' required for "date"
        super(Date, self).__init__({
                                       "type": "object",
                                       "properties": {
                                           "$date": {
                                               "type": "integer"
                                           }
                                       },
                                       "additionalProperties": False
                                   }, **kwargs)

    def formatter(self, value):
        return {"$date": int(calendar.timegm(value.utctimetuple()) * 1000)}

    def converter(self, value):
        # TODO support both $dateObj and ISO string formats
        return datetime.fromtimestamp(value["$date"] / 1000, timezone.utc)


class DateString(Raw):
    """
    Only accept ISO8601-formatted date strings.
    """

    def __init__(self, **kwargs):
        # TODO is a 'format' required for "date"
        super(DateString, self).__init__({"type": "string", "format": "date"}, **kwargs)

    def format(self, value):
        return value.strftime('%Y-%m-%d')

    def converter(self, value):
        return aniso8601.parse_date(value)


class DateTimeString(Raw):
    """
    Only accept ISO8601-formatted date-time strings.
    """

    def __init__(self, **kwargs):
        super(DateTimeString, self).__init__({"type": "string", "format": "date-time"}, **kwargs)

    def format(self, value):
        return value.isoformat()

    def converter(self, value):
        # FIXME enforce UTC
        return aniso8601.parse_datetime(value)


class Uri(String):
    def __init__(self, **kwargs):
        super(Uri, self).__init__(format="uri", **kwargs)


class Email(String):
    def __init__(self, **kwargs):
        super(Email, self).__init__(format="email", **kwargs)


class Boolean(Raw):
    def __init__(self, **kwargs):
        super(Boolean, self).__init__({"type": "boolean"}, **kwargs)

    def format(self, value):
        return bool(value)


class Integer(Raw):
    def __init__(self, minimum=None, maximum=None, default=None, **kwargs):
        schema = {"type": "integer"}

        if minimum is not None:
            schema['minimum'] = minimum
        if maximum is not None:
            schema['maximum'] = maximum

        super(Integer, self).__init__(schema, default=default, **kwargs)

    def formatter(self, value):
        return int(value)


class PositiveInteger(Integer):
    """
    A :class:`Integer` field that only accepts integers >=1.
    """

    def __init__(self, maximum=None, **kwargs):
        super(PositiveInteger, self).__init__(minimum=1, maximum=maximum, **kwargs)


class Number(Raw):
    def __init__(self,
                 minimum=None,
                 maximum=None,
                 exclusive_minimum=False,
                 exclusive_maximum=False,
                 **kwargs):

        schema = {"type": "number"}

        if minimum is not None:
            schema['minimum'] = minimum
            if exclusive_minimum:
                schema['exclusiveMinimum'] = True

        if maximum is not None:
            schema['maximum'] = maximum
            if exclusive_maximum:
                schema['exclusiveMaximum'] = True

        super(Number, self).__init__(schema, **kwargs)

    def formatter(self, value):
        return float(value)


class ToOne(Raw, ResourceBound):
    def __init__(self, resource, formatter=natural_keys.RefResolver(), **kwargs):
        self.reference = ResourceReference(resource)
        self._formatter = formatter

        def schema():
            target = self.target
            default_schema = formatter.schema(target)
            response_schema = default_schema

            # TODO support $id rather than $refObj
            # natural_keys = target.meta.natural_keys
            # if natural_keys:
            #     request_schema = {
            #         "anyOf": [default_schema] + [nk.schema(target) for nk in natural_keys]
            #     }
            # else:
            #     request_schema = default_schema
            return default_schema

        super(ToOne, self).__init__(schema, **kwargs)

    @cached_property
    def target(self):
        return self.reference.resolve(self.resource)

    def formatter(self, item):
        return self._formatter.format(self.target, item)

    def converter(self, value):
        return self._formatter.resolve(self.target, value)


class ToMany(Array):
    def __init__(self, resource, **kwargs):
        super(ToMany, self).__init__(ToOne(resource, nullable=False), **kwargs)


class Inline(Raw, ResourceBound):

    def __init__(self, resource, patch_instance=False, **kwargs):
        self.reference = ResourceReference(resource)
        self.patch_instance = patch_instance
        self.target = None

        def schema():
            if self.resource == self.target:
                return {"$ref": "#"}
            # FIXME complete with API prefix
            return {"$ref": self.resource.routes["schema"].rule_factory(self.resource)}

        super(Inline, self).__init__(schema, **kwargs)

    def bind(self, resource):
        super(Inline, self).bind(resource)
        self.target = self.reference.resolve(resource)

    def format(self, item):
        return self.target.schema.format(item)

    def convert(self, item):
        return self.target.schema.convert(item, patch_instance=self.patch_instance)


class ItemType(Raw):
    def __init__(self, resource):
        self.resource = resource
        super(ItemType, self).__init__(lambda: {
            "type": "string",
            "enum": [self.resource.meta.name]
        }, io="r")

    def format(self, value):
        return self.resource.meta.name


class ItemUri(Raw):
    def __init__(self, resource, attribute=None):
        self.resource = resource
        super(ItemUri, self).__init__(lambda: {
            "type": "string",
            "pattern": "^{}\/[^/]+$".format(re.escape(resource.route_prefix))
        }, io="r", attribute=attribute)

    def format(self, value):
        return '{}/{}'.format(self.resource.route_prefix, value)


class sa:
    class InlineModel(Object):
        def __init__(self, properties, model, **kwargs):
            super(sa.InlineModel, self).__init__(properties, **kwargs)
            self.model = model

        def converter(self, instance):
            instance = super(sa.InlineModel, self).converter(instance)
            # obj = EmbeddedJob.complete(super().convert(obj))
            # TODO commit()?
            if instance is not None:
                instance = self.model(**instance)
            return instance
