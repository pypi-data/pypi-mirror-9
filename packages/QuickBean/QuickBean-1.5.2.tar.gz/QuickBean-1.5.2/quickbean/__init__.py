#
#   Copyright 2014 Olivier Kozak
#
#   This file is part of QuickBean.
#
#   QuickBean is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
#   Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
#   any later version.
#
#   QuickBean is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
#   details.
#
#   You should have received a copy of the GNU Lesser General Public License along with QuickBean.  If not, see
#   <http://www.gnu.org/licenses/>.
#

import collections
import inspect
import json
import six


class AutoInit(object):
    """A decorator used to enhance the given class with an auto-generated initializer.

    To use this decorator, you just have to place it in front of your class :

    >>> import quickbean
    >>>
    >>> @quickbean.AutoInit('property_', 'other_property')
    ... class TestObject(object):
    ...     pass

    You will get an auto-generated initializer taking all the declared properties :

    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ... )
    >>>
    >>> test_object.property_
    'value'
    >>> test_object.other_property
    'otherValue'

    Note that it is also possible to declare default values :

    >>> @quickbean.AutoInit('property_', ('other_property', 'defaultValue'))
    ... class TestObject(object):
    ...     pass
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ... )
    >>>
    >>> test_object.property_
    'value'
    >>> test_object.other_property
    'defaultValue'

    Or, if you prefer something more explicit :

    >>> @quickbean.AutoInit('property_', quickbean.Argument('other_property', default='defaultValue'))
    ... class TestObject(object):
    ...     pass
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ... )
    >>>
    >>> test_object.property_
    'value'
    >>> test_object.other_property
    'defaultValue'

    """
    def __init__(self, *properties):
        self.properties = properties

    def __call__(self, bean_class):
        namespace = {}

        # noinspection PyShadowingNames
        def to_property_declaration_statement(index_and_property):
            index, property_ = index_and_property

            if isinstance(property_, tuple):
                default_value_name = 'default_value_%i' % index
                namespace[default_value_name] = property_[1]

                return '{property_}={default_value}'.format(property_=property_[0], default_value=default_value_name)
            else:
                return '{property_}'.format(property_=property_)

        # noinspection PyShadowingNames
        def to_property_initialization_statement(property_):
            if isinstance(property_, tuple):
                return 'self.{property_} = {property_}'.format(property_=property_[0])
            else:
                return 'self.{property_} = {property_}'.format(property_=property_)

        template = '\n'.join([
            'def __init__(self, %s):' % ', '.join(map(to_property_declaration_statement, enumerate(self.properties))),
            '\n'.join(['\t%s' % to_property_initialization_statement(property_) for property_ in self.properties]),
        ])

        six.exec_(template, namespace)

        bean_class.__init__ = namespace['__init__']

        return bean_class


class AutoInitFromJson(object):
    """A decorator used to enhance the given class with an auto-generated JSON decoder.

    To use this decorator, you just have to place it in front of your class :

    >>> import quickbean
    >>>
    >>> @quickbean.AutoInitFromJson
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property

    You will get an auto-generated JSON decoder :

    >>> test_object = TestObject.from_json_str('{"other_property": "otherValue", "property_": "value"}')
    >>>
    >>> str(test_object.property_)
    'value'
    >>> str(test_object.other_property)
    'otherValue'

    Many frameworks handle JSON with dictionaries, so you never have to parse JSON strings directly. In that case, you
    should use the 'from_json_dict' method instead :

    >>> test_object = TestObject.from_json_dict({'other_property': 'otherValue', 'property_': 'value'})
    >>>
    >>> str(test_object.property_)
    'value'
    >>> str(test_object.other_property)
    'otherValue'

    This decorator relies on the standard JSON decoder (https://docs.python.org/2/library/json.html). Values are then
    decoded according to this JSON decoder. But sometimes, it may be useful to customize how to decode some particular
    properties. This is done with types. Types are entities set to fields named as the corresponding properties suffixed
    with '_json_type' that decode the taken property value through the available 'from_json_str' method :

    >>> class CustomJsonType(object):
    ...     # noinspection PyMethodMayBeStatic
    ...     def from_json_str(self, value):
    ...         return '%sFromJson' % json.loads(value)
    >>>
    >>> @quickbean.AutoInitFromJson
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...
    ...     other_property_json_type = CustomJsonType()
    >>>
    >>> test_object = TestObject.from_json_str('{"other_property": "otherValue", "property_": "value"}')
    >>>
    >>> str(test_object.property_)
    'value'
    >>> str(test_object.other_property)
    'otherValueFromJson'

    If you prefer handle JSON with dictionaries, use the 'from_json_dict' method instead :

    >>> class CustomJsonType(object):
    ...     # noinspection PyMethodMayBeStatic
    ...     def from_json_dict(self, value):
    ...         return '%sFromJson' % value
    >>>
    >>> @quickbean.AutoInitFromJson
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...
    ...     other_property_json_type = CustomJsonType()
    >>>
    >>> test_object = TestObject.from_json_str('{"other_property": "otherValue", "property_": "value"}')
    >>>
    >>> str(test_object.property_)
    'value'
    >>> str(test_object.other_property)
    'otherValueFromJson'

    And if you have inner objects to map, you may simply use types like this :

    >>> @quickbean.AutoInitFromJson
    ... class InnerTestObject(object):
    ...     def __init__(self, property_, other_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    >>>
    >>> @quickbean.AutoInitFromJson
    ... class TestObject(object):
    ...     def __init__(self, inner):
    ...         self.inner = inner
    ...
    ...     inner_json_type = InnerTestObject
    >>>
    >>> test_object = TestObject.from_json_str('{"inner": {"other_property": "otherValue", "property_": "value"}}')
    >>>
    >>> str(test_object.inner.property_)
    'value'
    >>> str(test_object.inner.other_property)
    'otherValue'

    Sometimes, it may be very useful to directly decode a list of objects instead of having to decode them one by one.
    This is done through the 'list_from_json_str' method :

    >>> @quickbean.AutoInitFromJson
    ... class TestObject(object):
    ...     def __init__(self, property_):
    ...         self.property_ = property_
    >>>
    >>> test_objects = TestObject.list_from_json_str('[{"property_": "value"}, {"property_": "otherValue"}]')
    >>>
    >>> str(test_objects[0].property_)
    'value'
    >>> str(test_objects[1].property_)
    'otherValue'

    """
    def __new__(cls, bean_class):
        # noinspection PyShadowingNames
        def from_json_dict(cls, json_dict):
            for property_, value in dict(json_dict).items():
                if hasattr(cls, '%s_json_type' % property_):
                    type_ = getattr(cls, '%s_json_type' % property_)

                    if hasattr(type_, 'from_json_dict'):
                        json_dict[property_] = type_.from_json_dict(value)
                    if hasattr(type_, 'from_json_str'):
                        json_dict[property_] = type_.from_json_str(json.dumps(value))

            return cls(**json_dict)

        # noinspection PyShadowingNames
        def list_from_json_dict(cls, json_dict):
            return list(map(cls.from_json_dict, json_dict))

        # noinspection PyShadowingNames
        def from_json_str(cls, json_str):
            return cls.from_json_dict(json.loads(json_str))

        # noinspection PyShadowingNames
        def list_from_json_str(cls, json_str):
            return cls.list_from_json_dict(json.loads(json_str))

        bean_class.from_json_dict = classmethod(from_json_dict)
        bean_class.list_from_json_dict = classmethod(list_from_json_dict)
        bean_class.from_json_str = classmethod(from_json_str)
        bean_class.list_from_json_str = classmethod(list_from_json_str)

        return bean_class


class AutoBean(object):
    """A decorator used to enhance the given class with an auto-generated equality, representation, cloning method and
    JSON encoder.

    To use this decorator, you just have to place it in front of your class :

    >>> import quickbean
    >>>
    >>> @quickbean.AutoBean
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self._hidden_property = _hidden_property

    Which is strictly equivalent as :

    >>> @quickbean.AutoEq
    ... @quickbean.AutoRepr
    ... @quickbean.AutoClone
    ... @quickbean.AutoToDict
    ... @quickbean.AutoToJson
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self._hidden_property = _hidden_property

    """
    def __new__(cls, bean_class_or_filter):
        def with_properties_filter(properties_filter):
            def decorate_bean_class(bean_class):
                bean_class = AutoEq(properties_filter)(bean_class)
                bean_class = AutoRepr(properties_filter)(bean_class)
                bean_class = AutoClone(properties_filter)(bean_class)
                bean_class = AutoToDict(properties_filter)(bean_class)
                bean_class = AutoToJson(properties_filter)(bean_class)

                return bean_class

            return decorate_bean_class

        if inspect.isclass(bean_class_or_filter):
            return with_properties_filter(exclude_hidden_properties())(bean_class_or_filter)
        else:
            return with_properties_filter(bean_class_or_filter)


class AutoEq(object):
    """A decorator used to enhance the given class with an auto-generated equality.

    To use this decorator, you just have to place it in front of your class :

    >>> import quickbean
    >>>
    >>> @quickbean.AutoEq
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self._hidden_property = _hidden_property

    You will get an auto-generated equality taking all the properties available from your class :

    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='hiddenValue',
    ... )
    >>>
    >>> test_object == TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='differentHiddenValue',
    ... )
    True
    >>>
    >>> test_object == TestObject(
    ...     property_='value',
    ...     other_property='differentOtherValue',
    ...     _hidden_property='differentHiddenValue',
    ... )
    False

    An interesting thing to note here is that hidden properties -i.e. properties that begin with an underscore- are not
    taken into account.

    It is also possible to exclude arbitrary properties with the 'exclude_properties' filter :

    >>> @quickbean.AutoEq(quickbean.exclude_properties('excluded_property'))
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, excluded_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self.excluded_property = excluded_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     excluded_property='excludedValue',
    ... )
    >>>
    >>> test_object == TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     excluded_property='differentExcludedValue',
    ... )
    True

    If you prefer, it is even possible to do the opposite, that is to say, specifying the only properties to include
    with the 'only_include_properties' filter :

    >>> @quickbean.AutoEq(quickbean.only_include_properties('property_', 'other_property'))
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, non_included_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self.non_included_property = non_included_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     non_included_property='nonIncludedValue',
    ... )
    >>>
    >>> test_object == TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     non_included_property='differentNonIncludedValue',
    ... )
    True

    """
    def __new__(cls, bean_class_or_filter):
        def with_properties_filter(properties_filter):
            def decorate_bean_class(bean_class):
                def __eq__(self, other):
                    if other is not None and self.__class__ is other.__class__:
                        visible_properties = {
                            property_: self.__dict__[property_]
                            for property_ in self.__dict__ if properties_filter(property_)
                        }
                        other_visible_properties = {
                            property_: other.__dict__[property_]
                            for property_ in other.__dict__ if properties_filter(property_)
                        }

                        return visible_properties == other_visible_properties
                    else:
                        return False

                def __ne__(self, other):
                    return not self.__eq__(other)

                bean_class.__eq__ = __eq__
                bean_class.__ne__ = __ne__

                return bean_class

            return decorate_bean_class

        if inspect.isclass(bean_class_or_filter):
            return with_properties_filter(exclude_hidden_properties())(bean_class_or_filter)
        else:
            return with_properties_filter(bean_class_or_filter)


class AutoRepr(object):
    """A decorator used to enhance the given class with an auto-generated representation.

    To use this decorator, you just have to place it in front of your class :

    >>> import quickbean
    >>>
    >>> @quickbean.AutoRepr
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self._hidden_property = _hidden_property

    You will get an auto-generated representation taking all the properties available from your class :

    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='hiddenValue',
    ... )
    >>>
    >>> repr(test_object)
    "TestObject(other_property='otherValue', property_='value')"

    An interesting thing to note here is that hidden properties -i.e. properties that begin with an underscore- are not
    taken into account.

    It is also possible to exclude arbitrary properties with the 'exclude_properties' filter :

    >>> @quickbean.AutoRepr(quickbean.exclude_properties('excluded_property'))
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, excluded_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self.excluded_property = excluded_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     excluded_property='excludedValue',
    ... )
    >>>
    >>> repr(test_object)
    "TestObject(other_property='otherValue', property_='value')"

    If you prefer, it is even possible to do the opposite, that is to say, specifying the only properties to include
    with the 'only_include_properties' filter :

    >>> @quickbean.AutoRepr(quickbean.only_include_properties('property_', 'other_property'))
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, non_included_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self.non_included_property = non_included_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     non_included_property='nonIncludedValue',
    ... )
    >>>
    >>> repr(test_object)
    "TestObject(other_property='otherValue', property_='value')"

    """
    def __new__(cls, bean_class_or_filter):
        def with_properties_filter(properties_filter):
            def decorate_bean_class(bean_class):
                def __repr__(self):
                    visible_properties = {
                        property_: self.__dict__[property_]
                        for property_ in self.__dict__ if properties_filter(property_)
                    }

                    return '%s(%s)' % (self.__class__.__name__, ', '.join([
                        '%s=%r' % (property_, value) for property_, value in sorted(visible_properties.items())
                    ]))

                bean_class.__repr__ = __repr__

                return bean_class

            return decorate_bean_class

        if inspect.isclass(bean_class_or_filter):
            return with_properties_filter(exclude_hidden_properties())(bean_class_or_filter)
        else:
            return with_properties_filter(bean_class_or_filter)


class AutoClone(object):
    """A decorator used to enhance the given class with an auto-generated cloning method.

    To use this decorator, you just have to place it in front of your class :

    >>> import quickbean
    >>>
    >>> @quickbean.AutoClone
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property=None):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...
    ...         if _hidden_property:
    ...             self._hidden_property = _hidden_property

    You will get an auto-generated cloning method taking all the properties available from your class :

    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='hiddenValue',
    ... )
    >>>
    >>> test_object_clone = test_object.clone()
    >>>
    >>> sorted(test_object_clone.__dict__.items())
    [('other_property', 'otherValue'), ('property_', 'value')]

    An interesting thing to note here is that hidden properties -i.e. properties that begin with an underscore- are not
    taken into account.

    It is also possible to exclude arbitrary properties with the 'exclude_properties' filter :

    >>> @quickbean.AutoClone(quickbean.exclude_properties('excluded_property'))
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, excluded_property=None):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...
    ...         if excluded_property:
    ...             self.excluded_property = excluded_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     excluded_property='excludedValue',
    ... )
    >>>
    >>> test_object_clone = test_object.clone()
    >>>
    >>> sorted(test_object_clone.__dict__.items())
    [('other_property', 'otherValue'), ('property_', 'value')]

    If you prefer, it is even possible to do the opposite, that is to say, specifying the only properties to include
    with the 'only_include_properties' filter :

    >>> @quickbean.AutoClone(quickbean.only_include_properties('property_', 'other_property'))
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, non_included_property=None):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...
    ...         if non_included_property:
    ...             self.non_included_property = non_included_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     non_included_property='nonIncludedValue',
    ... )
    >>>
    >>> test_object_clone = test_object.clone()
    >>>
    >>> sorted(test_object_clone.__dict__.items())
    [('other_property', 'otherValue'), ('property_', 'value')]

    Note that it is also possible to override some of the properties on fly :

    >>> test_object_clone = test_object.clone(other_property='overriddenOtherValue')
    >>>
    >>> sorted(test_object_clone.__dict__.items())
    [('other_property', 'overriddenOtherValue'), ('property_', 'value')]

    """
    def __new__(cls, bean_class_or_filter):
        def with_properties_filter(properties_filter):
            def decorate_bean_class(bean_class):
                def clone(self, **overridden_properties):
                    visible_properties = {
                        property_: self.__dict__[property_]
                        for property_ in self.__dict__ if properties_filter(property_)
                    }

                    return self.__class__(**dict(
                        list(visible_properties.items()) + list(overridden_properties.items())
                    ))

                bean_class.clone = clone

                return bean_class

            return decorate_bean_class

        if inspect.isclass(bean_class_or_filter):
            return with_properties_filter(exclude_hidden_properties())(bean_class_or_filter)
        else:
            return with_properties_filter(bean_class_or_filter)


class AutoToDict(object):
    """A decorator used to enhance the given class with an auto-generated object to dict converter.

    To use this decorator, you just have to place it in front of your class :

    >>> import quickbean
    >>>
    >>> @quickbean.AutoToDict
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self._hidden_property = _hidden_property

    You will get an auto-generated object to dict converter taking all the properties available from your class :

    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='hiddenValue',
    ... )
    >>>
    >>> sorted(test_object.to_dict().items())
    [('other_property', 'otherValue'), ('property_', 'value')]

    An interesting thing to note here is that hidden properties -i.e. properties that begin with an underscore- are not
    taken into account.

    It is also possible to exclude arbitrary properties with the 'exclude_properties' filter :

    >>> @quickbean.AutoToDict(quickbean.exclude_properties('excluded_property'))
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, excluded_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self.excluded_property = excluded_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     excluded_property='excludedValue',
    ... )
    >>>
    >>> sorted(test_object.to_dict().items())
    [('other_property', 'otherValue'), ('property_', 'value')]

    If you prefer, it is even possible to do the opposite, that is to say, specifying the only properties to include
    with the 'only_include_properties' filter :

    >>> @quickbean.AutoToDict(quickbean.only_include_properties('property_', 'other_property'))
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, non_included_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self.non_included_property = non_included_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     non_included_property='nonIncludedValue',
    ... )
    >>>
    >>> sorted(test_object.to_dict().items())
    [('other_property', 'otherValue'), ('property_', 'value')]

    """
    def __new__(cls, bean_class_or_filter):
        def with_properties_filter(properties_filter):
            def decorate_bean_class(bean_class):
                def to_dict(self):
                    visible_properties = {
                        property_: self.__dict__[property_]
                        for property_ in self.__dict__ if properties_filter(property_)
                    }

                    return visible_properties

                bean_class.to_dict = to_dict

                return bean_class

            return decorate_bean_class

        if inspect.isclass(bean_class_or_filter):
            return with_properties_filter(exclude_hidden_properties())(bean_class_or_filter)
        else:
            return with_properties_filter(bean_class_or_filter)


class AutoToJson(object):
    """A decorator used to enhance the given class with an auto-generated JSON encoder.

    To use this decorator, you just have to place it in front of your class :

    >>> import quickbean
    >>>
    >>> @quickbean.AutoToJson
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self._hidden_property = _hidden_property

    You will get an auto-generated JSON encoder taking all the properties available from your class :

    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='hiddenValue',
    ... )
    >>>
    >>> test_object.to_json_str()
    '{"other_property": "otherValue", "property_": "value"}'

    Many frameworks handle JSON with dictionaries, so you never have to parse JSON strings directly. In that case, you
    should use the 'to_json_dict' method instead :

    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='hiddenValue',
    ... )
    >>>
    >>> list(sorted(test_object.to_json_dict().items()))
    [('other_property', 'otherValue'), ('property_', 'value')]

    An interesting thing to note here is that hidden properties -i.e. properties that begin with an underscore- are not
    taken into account.

    It is also possible to exclude arbitrary properties with the 'exclude_properties' filter :

    >>> @quickbean.AutoToJson(quickbean.exclude_properties('excluded_property'))
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, excluded_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self.excluded_property = excluded_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     excluded_property='excludedValue',
    ... )
    >>>
    >>> test_object.to_json_str()
    '{"other_property": "otherValue", "property_": "value"}'

    If you prefer, it is even possible to do the opposite, that is to say, specifying the only properties to include
    with the 'only_include_properties' filter :

    >>> @quickbean.AutoToJson(quickbean.only_include_properties('property_', 'other_property'))
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, non_included_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self.non_included_property = non_included_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     non_included_property='nonIncludedValue',
    ... )
    >>>
    >>> test_object.to_json_str()
    '{"other_property": "otherValue", "property_": "value"}'

    This decorator relies on the standard JSON encoder (https://docs.python.org/2/library/json.html). Values are then
    encoded according to this JSON encoder. But sometimes, it may be useful to customize how to encode some particular
    properties. This is done through methods named as the corresponding properties suffixed with '_to_json_str' :

    >>> @quickbean.AutoToJson
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self._hidden_property = _hidden_property
    ...
    ...     def other_property_to_json_str(self):
    ...         return json.dumps('%sToJson' % self.other_property)
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='hiddenValue',
    ... )
    >>>
    >>> test_object.to_json_str()
    '{"other_property": "otherValueToJson", "property_": "value"}'

    If you prefer handle JSON with dictionaries, use the '_to_json_dict' suffixed method instead :

    >>> @quickbean.AutoToJson
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self._hidden_property = _hidden_property
    ...
    ...     def other_property_to_json_dict(self):
    ...         return '%sToJson' % self.other_property
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='hiddenValue',
    ... )
    >>>
    >>> test_object.to_json_str()
    '{"other_property": "otherValueToJson", "property_": "value"}'

    This solution is quite simple, but it has a little drawback. Since it directly relies on the object's properties,
    the encoding code cannot be reused somewhere else. If you want your encoding code to be reusable, use types instead.
    Types are entities set to fields named as the corresponding properties suffixed with '_json_type' that encode the
    taken property value through the available 'to_json' method :

    >>> class CustomJsonType(object):
    ...     # noinspection PyMethodMayBeStatic
    ...     def to_json_str(self, value):
    ...         return json.dumps('%sToJson' % value)
    >>>
    >>> @quickbean.AutoToJson
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self._hidden_property = _hidden_property
    ...
    ...     other_property_json_type = CustomJsonType()
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='hiddenValue',
    ... )
    >>>
    >>> test_object.to_json_str()
    '{"other_property": "otherValueToJson", "property_": "value"}'

    If you prefer handle JSON with dictionaries, use the 'to_json_dict' method instead :

    >>> class CustomJsonType(object):
    ...     # noinspection PyMethodMayBeStatic
    ...     def to_json_dict(self, value):
    ...         return '%sToJson' % value
    >>>
    >>> @quickbean.AutoToJson
    ... class TestObject(object):
    ...     def __init__(self, property_, other_property, _hidden_property):
    ...         self.property_ = property_
    ...         self.other_property = other_property
    ...         self._hidden_property = _hidden_property
    ...
    ...     other_property_json_type = CustomJsonType()
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ...     other_property='otherValue',
    ...     _hidden_property='hiddenValue',
    ... )
    >>>
    >>> test_object.to_json_str()
    '{"other_property": "otherValueToJson", "property_": "value"}'

    Sometimes, it may be very useful to directly encode a list of objects instead of having to encode them one by one.
    This is done through the 'list_to_json_str' method :

    >>> @quickbean.AutoToJson
    ... class TestObject(object):
    ...     def __init__(self, property_):
    ...         self.property_ = property_
    >>>
    >>> test_object = TestObject(
    ...     property_='value',
    ... )
    >>> other_test_object = TestObject(
    ...     property_='otherValue',
    ... )
    >>>
    >>> TestObject.list_to_json_str(test_object, other_test_object)
    '[{"property_": "value"}, {"property_": "otherValue"}]'

    """
    def __new__(cls, bean_class_or_filter):
        def with_properties_filter(properties_filter):
            def decorate_bean_class(bean_class):
                def to_json_dict(self):
                    def value_to_json_dict(property_, value):
                        if hasattr(self, '%s_to_json_dict' % property_):
                            return getattr(self, '%s_to_json_dict' % property_)()
                        if hasattr(self, '%s_to_json_str' % property_):
                            return json.loads(getattr(self, '%s_to_json_str' % property_)())

                        if hasattr(self, '%s_json_type' % property_):
                            type_ = getattr(self, '%s_json_type' % property_)

                            if hasattr(type_, 'to_json_dict'):
                                return getattr(self, '%s_json_type' % property_).to_json_dict(value)
                            if hasattr(type_, 'to_json_str'):
                                return json.loads(getattr(self, '%s_json_type' % property_).to_json_str(value))

                        if hasattr(value, 'to_json_dict'):
                            return collections.OrderedDict(sorted(value.to_json_dict().items()))
                        if hasattr(value, 'to_json_str'):
                            return collections.OrderedDict(sorted(json.loads(value.to_json_str()).items()))

                        return value

                    visible_properties = {
                        property_: self.__dict__[property_]
                        for property_ in self.__dict__ if properties_filter(property_)
                    }

                    return collections.OrderedDict(
                        (property_, value_to_json_dict(property_, value))
                        for property_, value in sorted(visible_properties.items())
                    )

                # noinspection PyShadowingNames
                def list_to_json_dict(cls, *objects):
                    return list(map(cls.to_json_dict, objects))

                def to_json_str(self):
                    return json.dumps(self.to_json_dict())

                # noinspection PyShadowingNames
                def list_to_json_str(cls, *objects):
                    return json.dumps(cls.list_to_json_dict(*objects))

                bean_class.to_json_dict = to_json_dict
                bean_class.list_to_json_dict = classmethod(list_to_json_dict)
                bean_class.to_json_str = to_json_str
                bean_class.list_to_json_str = classmethod(list_to_json_str)

                return bean_class

            return decorate_bean_class

        if inspect.isclass(bean_class_or_filter):
            return with_properties_filter(exclude_hidden_properties())(bean_class_or_filter)
        else:
            return with_properties_filter(bean_class_or_filter)


def exclude_hidden_properties():
    return lambda property_: not property_.startswith('_')


def exclude_properties(*properties):
    return lambda property_: property_ not in properties


def only_include_properties(*properties):
    return lambda property_: property_ in properties


Argument = collections.namedtuple('Argument', 'name default')
