# -*- coding: utf-8 -*-
# Package placeholder

from __future__ import print_function

import itertools

from .inspect import get_valued_prototype, call_with_valued_prototype


def multi(margs):
    """Demultiply execution of a function along given argument.

    This offers support on specified argument of multiple values.

    For instance::

        >>> @multi('x')
        ... def foo(x):
        ...     print("I like %s." % x)

    Normal call is preserved::

        >>> foo('apples')
        I like apples.

    But now we can provide lists to the first argument, and this will
    call the underlying function for each subvalues::

        >>> foo(['carrot', 'steak', 'banana'])
        I like carrot.
        I like steak.
        I like banana.

    You can actualy given also multiple argument to ``mutli`` itself to
    specify several argument to support expantion::

        >>> @multi(['x', 'y'])
        ... def bar(x, y):
        ...     print("%s likes %s." % (x, y))

    Normal call is preserved::

        >>> bar('Jane', 'apples')
        Jane likes apples.

    But multiple calls are supported in both arguments::

        >>> bar(['Jane', 'Cheetah', 'Tarzan'], ['apples', 'banana'])
        Jane likes apples.
        Jane likes banana.
        Cheetah likes apples.
        Cheetah likes banana.
        Tarzan likes apples.
        Tarzan likes banana.

    Please also notice that multi will return None whatever the actual
    results of the inner function.

    """
    if not isinstance(margs, (tuple, list)):
        margs = [margs]

    def decorator(f):
        def _f(*a, **kw):
            prototype = get_valued_prototype(f, a, kw)
            all_mvalues = [prototype[marg] for marg in margs]
            all_mvalues = [v if isinstance(v, (tuple, list)) else [v]
                           for v in all_mvalues]
            ret = []
            for mvalues in itertools.product(*all_mvalues):
                prototype.copy()
                prototype.update(dict(zip(margs, mvalues)))
                ret.append(call_with_valued_prototype(f, prototype))
        return _f
    return decorator
