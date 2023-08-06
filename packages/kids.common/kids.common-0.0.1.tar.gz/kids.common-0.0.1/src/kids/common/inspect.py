# -*- coding: utf-8 -*-


from __future__ import absolute_import

import inspect
import collections


def get_arg_spec(f):
    args, varargs, keywords, defaults = inspect.getargspec(f)
    defaults = [] if defaults is None else defaults
    defaults = collections.OrderedDict(
        reversed(list(
            (k, v)
            for k, v in zip(reversed(args), reversed(defaults)))))
    return args, varargs, keywords, defaults


def get_valued_prototype(f, a, kw):
    """Returns an ordered dict of the label/value received by given function


    Returns the mapping applied to the function::

       >>> get_valued_prototype(lambda a, b: None, [1, 2], {})
       OrderedDict([('a', 1), ('b', 2)])

    So this means 'a' will be valuated with 1, etc...

    default values
    --------------

    It works also if you have default values::

       >>> get_valued_prototype(lambda a, b, c=None: None, [1, 2], {})
       OrderedDict([('a', 1), ('b', 2), ('c', None)])

       >>> get_valued_prototype(lambda a, b, c=None: None, [1, 2, 3], {})
       OrderedDict([('a', 1), ('b', 2), ('c', 3)])

    keyword values
    --------------

       >>> get_valued_prototype(
       ...     lambda a, b=None, c=None: None,
       ...     [1, ], {'c': 3})
       OrderedDict([('a', 1), ('b', None), ('c', 3)])

    """
    args, _varargs, _keywords, defaults = get_arg_spec(f)
    a = list(a)
    if defaults:
        a.extend(defaults.values())
    res = collections.OrderedDict(
        (label, a[idx]) for idx, label in enumerate(args))
    if kw:
        for k, v in kw.items():
            res[k] = v
    return res


def call_with_valued_prototype(f, valued_prototype):
    """Call and return the result of the given function applied to prototype


    For instance, here, we will call the lambda with the given values::

        >>> call_with_valued_prototype(
        ...     lambda a, b: "a: %s, b: %s" % (a, b),
        ...     {'a': 1, 'b': 2})
        'a: 1, b: 2'

    If you fail valuating all the necessary values, it should bail out with
    an exception::

        >>> call_with_valued_prototype(
        ...     lambda a, b: "a: %s, b: %s" % (a, b),
        ...     {'a': 1, 'c': 2})
        Traceback (most recent call last):
        ...
        ValueError: Missing value for argument 'b'.

    If you provide wrong values, it should fail as if you called it yourself::

        >>> call_with_valued_prototype(
        ...     lambda a, b: "a: %s, b: %s" % (a, b),
        ...     {'a': 1, 'b': 2, 'foo': 'bar'})
        Traceback (most recent call last):
        ...
        TypeError: '<lambda>' got unexpecteds keywords argument foo

    """
    args, _varargs, _keywords, defaults = get_arg_spec(f)
    build_args = []
    valued_prototype = valued_prototype.copy()
    for arg in args:
        if arg in valued_prototype:
            value = valued_prototype.pop(arg)
        else:
            try:
                value = defaults[arg]
            except KeyError:
                raise ValueError("Missing value for argument %r." % arg)
        build_args.append(value)
    if len(valued_prototype):
        raise TypeError("%r got unexpecteds keywords argument %s"
                        % (f.__name__, ", ".join(valued_prototype.keys())))
    return f(*build_args)
