# Absolute import (the default in a future Python release) resolves
# the collections import as the Python standard collections module
# rather than this module of the same name.
from __future__ import absolute_import
from copy import copy
from collections import (Iterable, Mapping, defaultdict)
import functools

def is_nonstring_iterable(obj):
    """
    :param obj: the object to check
    :return: whether the given object is a non-string iterable object
    """
    return isinstance(obj, Iterable) and not isinstance(obj, str)


def to_series(items, conjunction='and'):
    """
    Formats the given items as a series string.

    Example:

    >>> to_series([1, 2, 3])
    '1, 2 and 3'

    :param items: the items to format in a series
    :param conjunction: the series conjunction
    :return: the items series
    :rtype: str
    """
    if not items:
        return ''
    prefix = ', '.join([str(i) for i in items[:-1]])
    suffix = str(items[-1])
    if not prefix:
        return suffix
    else:
        return (' ' + conjunction + ' ').join([prefix, suffix])

def nested_defaultdict(factory, levels=0):
    """
    Makes a defaultdict for the given factory and number of levels, e.g.::

        >> from qiutil.collections import nested_defaultdict as dd
        >> dd(list, 0)[1]
        []
        >> dd(dict, 2)[1][2][3]
        {}

    Note that the default levels parameter value 0 is synonymous with the
    standard Python collections defaultdict, i.e.::

        dd(list)

    is the same as::

        dd(list, 0)

    or::

        from collections import defaultdict
        defaultdict(list)
    
    Thus, this ``nested_defaultdict`` function can serve as a drop-in
    replacement for ``defaultdict``.

    :param factory: the 0th level defaultdict factory.
    :param levels: the number of levels
    """
    # The recursive nested dictionary generator, where f is the factory
    # and n is the number of levels.
    dd = lambda f, n: defaultdict((lambda: dd(f, n - 1)) if n else f)

    return dd(factory, levels)


def update(target, *sources, **opts):
    """
    Updates the given target object from the given source objects.
    The target object can be a dictionary, list or set. The target
    and sources are validated for compatibility as follows:
    
    * If the target object is a Mapping, then the sources must
      be Mappings.
    
    * Otherwise, if the target object is a list or set, then the
      sources must be non-string iterables.
    
    The target is updated from the sources in order as follows:
    
    * If the target object is a Mapping and the *recursive* flag is
      falsey, then the standard Python dictionary update is applied.
    
    * If the target object is a Mapping and the *recursive* flag is
      truthy, then the update is applied recursively to nested
      dictionaries, e.g.:
      
      >> from qiutil.collections import update
      >> target = dict(a=dict(aa=1))
      >> update(target, dict(a=dict(aa=2, ab=3)))
      >> target
      {'a': {'aa': 2, 'ab': 3}}
    
    * If the target object is a list or set, then the source items
      which are not yet in the target are added to the target, e.g.:
    
      >> from qiutil.collections import update
      >> target = [1, 2, 2, 5]
      >> update(target, [4, 2, 6, 6])
      >> target
      [1, 2, 2, 5, 4, 6, 6]
    
    This function adapts the solution offered in a
    `StackOverflow post <http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth>`
    to support lists, sets and multiple sources.
    
    :param target: the dictionary to update
    :param sources: the update source dictionaries
    :param opts: the following keyword options:
    :keyword recursive: if True, then apply the update recursively to
        nested dictionaries
    """
    # Validate the sources.
    _validate_update_compatibility(target, *sources)
    # Make the update helper function. This idiom refactors the source
    # iteration block into a callable function with a sole source argument.
    # This pattern is a little obscure to those not well-versed in functional
    # programming, but it is cleaner than the alternative of embedding the
    # _updater logic into the source iteration.
    updater = _create_updater(target, **opts)
    # Apply the successive source updates.
    for source in sources:
        updater(source)


def _create_updater(target, **opts):
    """
    :param target: the update target
    :param opts: the following keyword options:
    :keyword recursive: if True, then apply the update recursively to
        nested dictionaries
    :return: the function to apply to a *source* argument
    """
    if isinstance(target, Mapping):
        if opts.get('recursive'):
            return functools.partial(_update_dict_recursive, target)
        else:
            # Apply the standard Python dictionary update.
            return lambda src: target.update(src)
    else:
        return functools.partial(_update_collection, target)


def _update_dict_recursive(target, source):
    for key, srcval in source.iteritems():
        if key in target:
            tgtval = target[key]
            # If the target value can be merged from the source
            # value, then replace the target value with a shallow
            # copy and update it recursively.
            if isinstance(tgtval, Mapping) and isinstance(srcval, Mapping):
                target[key] = tgtval = copy(tgtval)
                _update_dict_recursive(tgtval, srcval)
                continue
        # Set the target item.
        target[key] = copy(srcval)


def _validate_update_compatibility(target, *sources):
    if isinstance(target, Mapping):
        for source in sources:
            if not isinstance(source, Mapping):
                raise TypeError("Update source is incompatible with the"
                                " dictionary target: %s" % source)
    elif isinstance(target, list) or isinstance(target, set):
        for source in sources:
            if not is_nonstring_iterable(source):
                raise TypeError("Update source is incompatible with the"
                                " collection target: %s" % source)
    else:
        raise TypeError("Update target is type is not supported: %s" % target)


def _update_collection(target, source):
    """
    Adds to the target those source items which are not
    yet in the target, as described in :meth:`update`.
    
    :param target: the list or set to update
    :param source: the input non-string iterable
    :raise TypeError: if the target is neither a list or set
    """
    if isinstance(target, set):
        target.update(source)
    elif isinstance(target, list):
        exclude = set(target)
        diff = (item for item in source if item not in exclude)
        target.extend(diff)
    else:
        raise TypeError("Update target type not supported")


class ImmutableDict(dict):

    """
    ImmutableDict is a dictionary that cannot be changed after creation.

    An ImmutableDict is *not* hashable and therefore cannot be used as a
    dictionary key or set member. See http://www.python.org/dev/peps/pep-0351
    for the rationale.
    """

    def __init__(self, *args, **kwargs):
        super(ImmutableDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        """
        :raise NotImplementedError: always
        """
        raise NotImplementedError("The dictionary is immutable: %s" % self)


EMPTY_DICT = ImmutableDict()
"""
An immutable empty dictionary.
This constant serves as an efficient method return default value.
"""
