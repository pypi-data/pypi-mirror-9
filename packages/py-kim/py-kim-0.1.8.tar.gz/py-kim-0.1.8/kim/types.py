#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import date, datetime
import iso8601
import re
import decimal
import inspect
import importlib

from .exceptions import ValidationError, ConfigurationError
from .mapping import get_attribute, serialize, BaseMapping, marshal

from kim.utils import is_valid_type


def iskimtype(type_):
    return isinstance(type_, BaseType)


class BaseType(object):
    """:py:class:`.BaseType` defines the default ``Type`` api used by all
    kim types.
    """

    __visit_name__ = 'default'

    _kim_type = True

    error_message = 'An error ocurred validating this field'

    def get_error_message(self, value):
        """Return a valiation error message for this Type

        :returns: an error message explaining the error that occured
        """
        return unicode(self.error_message)

    def marshal_value(self, value):
        """called during marshaling of data.

        This method provides a hook for types to perform additonal operations
        on the ``value`` being marshaled.

        :rtype: mixed
        :returns: ``value``
        """

        return value

    def serialize_value(self, value):
        """called during serialization of data.

        This method provides a hook for types to perform additonal operations
        on the ``value`` being serialized.

        :rtype: mixed
        :returns: ``value``
        """

        return value

    def validate(self, value):
        """Validate that ``value`` is valid. If ``value``
        is invalid a :py:class:`kim.exceptions.ValidationError`
        will be raised e.g::

            def validate(self, value):
                if not isinstance(value, str):
                    raise ValidationError("Invalid type")

        :param value: the value being validated.

        :raises: :py:class:`kim.exceptions.ValidationError`
        :rtype: boolean
        :returns: True
        """

        return True


class TypedType(BaseType):
    """This type provides the base functionality for types that expect a
    specific python type e.g and :py:class:`.Integer` or :py:class:`.String`.
    """

    type_ = None

    error_message = 'This field was of an incorrect type'

    def __init__(self, *args, **kwargs):
        """Create a new :py:class:`.TypedType` constructed from ``args``
        and ``kwargs``.

        :param choices: provide a list of valid values for this type.  When
            validating this type the value will be checked to ensure its an
            allowed choice.

        """
        self.choices = kwargs.pop('choices', None)
        for k in kwargs:
            if k in ('name', 'field_type', 'source', 'field_id', 'default',
                     'required', 'read_only', 'allow_none'):
                raise ConfigurationError('Type %s was not expecting argument %s. ' \
                        'Did you mean to pass this to Field instead?' % (
                        self.__class__.__name__, k))
        super(TypedType, self).__init__(*args, **kwargs)

    def validate(self, value):
        """validates that ``value`` is of a given type

        .. seealso::
            * :py:meth:`kim.types.BaseType.validate`

        :raises: :class:`kim.exceptions.ValidationError`
        :returns: None
        """

        if value is not None:
            if not isinstance(value, self.type_):
                raise ValidationError(self.get_error_message(value))

            # TODO this should be moved to the ``Field`` api.
            if self.choices and value not in self.choices:
                raise ValidationError('not a valid choice')

        return True


class String(TypedType):
    """a ``TypedType`` that validate the incoming value is a valid ``str``
    """

    type_ = basestring


class Integer(TypedType):
    """a ``TypedType`` that validates the incoming value is a valid ``int``.
    """

    type_ = int


class Boolean(TypedType):
    """a ``TypedType`` that validates the incoming value is a valid ``bool``.
    """

    type_ = bool


class NumericType(BaseType):
    """a :py:class:`.TypedType` that allows integers to be passed as strings
    as well as standard ints.

    """

    type_ = int

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        super(NumericType, self).__init__(*args, **kwargs)

    def validate(self, value):
        """validates that value is a valid int or can be converted to an int.

        .. seealso::
            :meth:`kim.types.BaseType.validate`

        :raises: :py:class:`kim.exceptions.ValidationError`
        :rtype: bool
        :returns: True
        """

        if value is not None:

            if (isinstance(value, basestring)
                    and not value.isdigit()):
                raise ValidationError(self.get_error_message(value))

            try:
                int(value)
            except ValueError:
                raise ValidationError(self.get_error_message(value))

            if self.choices and value not in self.choices:
                raise ValidationError('not a valid choice')

        return True


class PositiveInteger(Integer):
    """a ``TypedType`` that validates its value is an integer and that the value
    is not less than zero.
    """

    def validate(self, value):
        """validate that ``value`` is an integer and that it is not less
        than zero.

        :param value: value to be validated.
        """
        super(PositiveInteger, self).validate(value)
        if value is not None and value < 0:
            raise ValidationError('must be positive integer')

        return True


class Nested(BaseType):
    """Create a :py:class:`.Nested` mapping from a
    :py:class:`kim.mapping.BaseMapping` or from a mapped
    :py:class:`kim.serializers.Serializer` that allows users to create complex
    re-usable data structures in kim e.g::

        food = Mapping(Field('type', String()),
                       Field('name', String()))

        user_mapping = Mapping(Field('name', String()),
                               Field('foods', Nested(food_mapping))

    a :py:class:`.Nested` type may also specify a role to allow flexibly
    changing the types returned from a nested mapping.
    This further increases the flexibilty and reusability of mappings.
    For example, in certain cases when we want to re-use our food mapping
    in another mapping, we might not always want to return the
    'type' field. e.g::

        public_food_role = Role('public', 'name')
        user_mapping = Mapping(Field('name', String()),
                               Field('foods', Nested(food_mapping,
                                      role=public_food_role))

    In this example only the `name` field from the food mapping would be
    included in the returned data.

    .. seealso::

        * :py:class:`.BaseType`
        * :py:class:`kim.roles.Role`

    """

    __visit_name__ = 'nested'


    def __init__(self, mapped=None, role=None, *args, **kwargs):
        """:class:`Nested`

        :param name: name of this :py:class:`.Nested` type
        :param mapped: a :py:class:`kim.mapping.Mapping` or Mapped
            Serializer instance
        :param role: :py:class:`kim.roles.Role` role

        """

        self._mapping = None
        self.mapping = mapped
        self.role = role

        super(Nested, self).__init__(*args, **kwargs)

    @property
    def mapping(self):
        """Getter property to retrieve the mapping for this `Nested` type.

        :returns: self._mapping
        """
        # Allow mappings to be passed as a string if they don't exist yet
        # The setter has already done most of the work in getting the module,
        # but we need to actually resolve it here.
        if isinstance(self._mapping, str):
            self._mapping = getattr(self._mapping_module, self._mapping)

        if inspect.isclass(self._mapping):
            # Instantiate the class if not already
            self._mapping = self._mapping()

        try:
            mapping = self._mapping.__mapping__
        except AttributeError:
            mapping = self._mapping

        if not isinstance(mapping, BaseMapping):
            raise TypeError('Nested() must be called with a '
                            'mapping or a mapped serializer class or a mapped'
                            'serializer instance or a python path to one'
                            'of the above')
        return mapping

    @mapping.setter
    def mapping(self, mapped):
        """Setter for mapping property

        the :param:`mapped` arg must be a valid
        :class:`kim.mapping.BaseMapping` instance or any object exposing a
        __mapping__ attribute.

        :raises: TypeError
        """
        # Allow mappings to be passed as a string if they don't exist yet
        # see http://stackoverflow.com/questions/1095543/get-name-of-calling-functions-module-in-python
        # We store the module it came from here, but we don't actually resolve
        # the path until we need to access the mapping, because it won't be
        # in scope until then.
        if isinstance(mapped, str):
            if '.' in mapped:
                # A full python path has been passed
                module = '.'.join(mapped.split('.')[:-1])
                mapped = mapped.split('.')[-1]
                self._mapping_module = importlib.import_module(module)
            else:
                # Only a relative name has been passed, assume it's in
                # the same module who called us
                constructor_called_from = inspect.stack()[2]
                called_from_module = inspect.getmodule(constructor_called_from[0])
                self._mapping_module = called_from_module

        self._mapping = mapped

    def get_mapping(self):
        """Return the mapping defined for this `Nested` type.

        If a `role` has been passed to the `Nested` type the mapping
        will be run through the role automatically

        :returns: :class:`kim.mapping.BaseMapping` type

        .. seealso::
            :class:`kim.roles.Role`
        """
        if self.role:
            return self.role.get_mapping(self.mapping)

        return self.mapping

    def marshal_value(self, source_value):
        """marshal the `mapping` for this nested type

        :param source_value: data to marshal this `Nested` type to

        :returns: marshalled mapping
        """
        return marshal(self.get_mapping(), source_value)

    def serialize_value(self, source_value):
        """serialize `source_value` for this NestedType's mapping.

        :param source_value: data to serialize this `Nested` type to

        :returns: serialized mapping
        """
        return serialize(self.get_mapping(), source_value)

    def validate(self, source_value):
        """iterates Nested mapping calling validate for each
        field in the mapping.  Errors from each field will be stored
        and finally raised in a collection of errors

        :raises: ValidationError
        :returns: True
        """
        errors = defaultdict(list)

        for field in self.get_mapping().fields:
            value = get_attribute(source_value, field.name)
            try:
                field.is_valid(value)
            except ValidationError as e:
                errors[field.name].append(e.message)

        if errors:
            raise ValidationError(errors)
        else:
            return super(Nested, self).validate(source_value)


class Collection(TypedType):

    type_ = list

    __visit_name__ = 'collection'

    def __init__(self, inner_type, *args, **kwargs):
        self.inner_type = inner_type
        self.serialize_member = kwargs.pop('serialize_member', None)
        self.marshal_member = kwargs.pop('marshal_member', None)
        if not is_valid_type(self.inner_type):
            raise TypeError("Collection() requires a valid Type "
                            "as its first argument")
        super(Collection, self).__init__(*args, **kwargs)

    def serialize_members(self, source_value):
        if self.serialize_member:
            return [self.serialize_member(member) for member in source_value]
        else:
            if source_value is None:
                return []
            else:
                return source_value

    def marshal_members(self, source_value):
        if self.marshal_member:
            return [self.marshal_member(member) for member in source_value]
        else:
            if source_value is None:
                return []
            else:
                return source_value

    def marshal_value(self, source_value):

        return [self.inner_type.marshal_value(member)
                for member in self.marshal_members(source_value)]

    def serialize_value(self, source_value):

        return [self.inner_type.serialize_value(member)
                for member in self.serialize_members(source_value)]

    def validate(self, source_value):
        """Call :meth:`validate` on `type`.

        """
        super(Collection, self).validate(source_value)
        if source_value is not None:
            return [self.inner_type.validate(mem) for mem in source_value]


class DateTime(BaseType):
    type_ = datetime

    def serialize_value(self, source_value):
        if source_value is not None:
            return source_value.isoformat()

    def marshal_value(self, source_value):
        return iso8601.parse_date(source_value)

    def validate(self, source_value):
        super(DateTime, self).validate(source_value)
        if source_value is not None:
            try:
                iso8601.parse_date(source_value)
            except iso8601.ParseError:
                raise ValidationError('Date must be in iso8601 format')
        return True


class Date(DateTime):

    type_ = date

    def marshal_value(self, source_value):
        return super(Date, self).marshal_value(source_value).date()


class Regexp(String):

    def __init__(self, *args, **kwargs):
        self.pattern = kwargs.pop('pattern', re.compile('.*'))
        super(Regexp, self).__init__(*args, **kwargs)

    def validate(self, source_value):
        super(Regexp, self).validate(source_value)
        if source_value is not None and not self.pattern.match(source_value):
            raise ValidationError('Does not match regexp')
        return True


ipv4_re = re.compile(
    r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')
validate_ipv4_address = Regexp(pattern=ipv4_re).validate


# TODO handle validation ipv6 domains.
def validate_ipv46_address(value):
    try:
        validate_ipv4_address(value)
    except ValidationError as e:
        raise e


class Email(String):
    # Django from django forms

    message = 'Enter a valid email address.'

    user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"$)',  # quoted-string
        re.IGNORECASE)
    domain_regex = re.compile(
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|[A-Z0-9-]{2,})$',
        re.IGNORECASE)
    literal_regex = re.compile(
        # literal form, ipv4 or ipv6 address (SMTP 4.1.3)
        r'\[([A-f0-9:\.]+)\]$',
        re.IGNORECASE)

    domain_whitelist = ['localhost']

    def __init__(self, message=None, whitelist=None, *args, **kwargs):
        super(Email, self).__init__(*args, **kwargs)
        if message is not None:
            self.message = message
        if whitelist is not None:
            self.domain_whitelist = whitelist

    def validate(self, source_value):

        if not source_value or '@' not in source_value:
            raise ValidationError(self.message)

        user_part, domain_part = source_value.rsplit('@', 1)

        if not self.user_regex.match(user_part):
            raise ValidationError(self.message)

        if (domain_part not in self.domain_whitelist and
                not self.validate_domain_part(domain_part)):
            # Try for possible IDN domain-part
            try:
                domain_part = domain_part.encode('idna').decode('ascii')
                if self.validate_domain_part(domain_part):
                    return True
            except UnicodeError:
                pass
            raise ValidationError(self.message)

        return True

    def validate_domain_part(self, domain_part):
        if self.domain_regex.match(domain_part):
            return True

        literal_match = self.literal_regex.match(domain_part)
        if literal_match:
            ip_address = literal_match.group(1)
            try:
                validate_ipv46_address(ip_address)
                return True
            except ValidationError:
                pass
        return False


class Float(BaseType):

    def __init__(self, *args, **kwargs):
        self.as_string = kwargs.pop('as_string', False)
        super(Float, self).__init__(*args, **kwargs)

    def validate(self, source_value):
        super(Float, self).validate(source_value)
        if source_value is not None:
            if self.as_string:
                if not isinstance(source_value, str):
                    raise ValidationError(self.get_error_message(source_value))

                # Now just check we can cast it to a float
                try:
                    float(source_value)
                except ValueError:
                    raise ValidationError('Not a valid float')
            else:
                if not isinstance(source_value, float):
                    raise ValidationError(self.get_error_message(source_value))
        return True

    def serialize_value(self, source_value):
        if self.as_string:
            return str(source_value)
        else:
            return source_value

    def marshal_value(self, source_value):
        return float(source_value)


class Decimal(BaseType):
    type_ = decimal.Decimal

    def __init__(self, *args, **kwargs):
        decimals = kwargs.pop('precision', 5)
        self.precision = decimal.Decimal('0.' + '0' * (decimals - 1) + '1')
        super(Decimal, self).__init__(*args, **kwargs)

    def _cast(self, value):
        if value is not None and value != '':
            return decimal.Decimal(value).quantize(self.precision)

    def validate(self, source_value):
        super(Decimal, self).validate(source_value)
        # Now just check we can cast it to a Decimal
        try:
            self._cast(source_value)
        except decimal.InvalidOperation:
            raise ValidationError('Not a valid decimal')

        return True

    def serialize_value(self, source_value):
        result = self._cast(source_value)
        if result is not None:
            return str(result)

    def marshal_value(self, source_value):
        return self._cast(source_value)
