QuickBean is a library that reduces the boilerplate code required to define beans.

Installation
============

Here is how to install QuickBean : ::

    pip install quickbean

Starting with QuickBean
=======================

Suppose you have defined the following bean :

.. code:: python

    >>> class MyObject(object):
    >>>     def __init__(self, my_property, my_other_property):
    >>>         self.my_property = my_property
    >>>         self.my_other_property = my_other_property

If you would like your bean to have a human-readable representation, you have to override the *__repr__* method :

.. code:: python

    >>> class MyObject(object):
    >>>     def __init__(self, my_property, my_other_property):
    >>>         self.my_property = my_property
    >>>         self.my_other_property = my_other_property
    >>>
    >>>     def __repr__(self):
    >>>         return 'MyObject(my_property=%s, my_other_property=%s)' % (self.my_property, self.my_other_property)

If you would like your bean to be equality comparable, you also have to override the *__eq__* and *__ne__* methods :

.. code:: python

    >>> class MyObject(object):
    >>>     def __init__(self, my_property, my_other_property):
    >>>         self.my_property = my_property
    >>>         self.my_other_property = my_other_property
    >>>
    >>>     def __repr__(self):
    >>>         return 'MyObject(my_property=%s, my_other_property=%s)' % (self.my_property, self.my_other_property)
    >>>
    >>>     def __eq__(self, other):
    >>>         return other.__class__ is MyObject and other.__dict__ == self.__dict__
    >>>
    >>>     def __ne__(self, other):
    >>>         return not self.__eq__(other)

Although there is nothing difficult here, it would be better if this boilerplate code could be automatically generated
for you. This is exactly what QuickBean brings to you :

.. code:: python

    >>> import quickbean
    >>>
    >>> @quickbean.AutoBean
    >>> class MyObject(object):
    >>>     def __init__(self, my_property, my_other_property):
    >>>         self.my_property = my_property
    >>>         self.my_other_property = my_other_property

You may even let QuickBean generate the *__init__* method for you :

.. code:: python

    >>> import quickbean
    >>>
    >>> @quickbean.AutoInit('my_property', 'my_other_property')
    >>> @quickbean.AutoBean
    >>> class MyObject(object):
    >>>     pass

Documentation
=============

See the `online documentation`_ for more information on how to use QuickBean.

.. _`online documentation`: http://quickbean.readthedocs.org/en/latest/

Changelog
=========

QuickBean 1.5
-------------

Here are the changes made from QuickBean 1.4 :

- Ability to directly encode/decode list of objects through JSON.
- The *AutoInit* decorator now accepts the default values to be specified using a more explicit form.

QuickBean 1.4
-------------

Here are the changes made from QuickBean 1.3 :

- Implementation of the *AutoToDict* decorator.

QuickBean 1.3
-------------

**This release breaks compatibility with QuickBean 1.2.** See below for more information.

Here are the changes made from QuickBean 1.2 :

- Ability to declare default values from the *AutoInit* decorator.
- Implementation of the *AutoClone* decorator.
- The properties filters can now be customized with less boilerplate code (**breaks compatibility**).

QuickBean 1.2
-------------

**This release breaks compatibility with QuickBean 1.1.** See below for more information.

Here are the changes made from QuickBean 1.1 :

- Changing how the *AutoInitFromJson*, *AutoBean*, *AutoEq*, *AutoRepr* and *AutoToJson* decorators are applied to
  beans' classes (**breaks compatibility**).
- The decorators now modify beans' classes themselves instead of decorating them.
- Renaming all the *to_json* methods -including suffixed ones- to *to_json_str* (**breaks compatibility**).
- Ability to handle JSON with dictionaries instead of strings.

QuickBean 1.1
-------------

**This release breaks compatibility with QuickBean 1.0.** See below for more information.

Here are the changes made from QuickBean 1.0 :

- Renaming the *AutoJson* decorator to *AutoToJson* (**breaks compatibility**).
- Implementation of the *AutoInitFromJson* decorator.
- Ability to define custom JSON types to encode and decode properties.
- Making the *_to_json* conversion method consistent with JSON types (**breaks compatibility**).

QuickBean 1.0
-------------

First release of QuickBean.
