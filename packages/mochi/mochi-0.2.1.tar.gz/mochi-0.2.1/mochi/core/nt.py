from keyword import iskeyword as _iskeyword
import sys as _sys
import six


_class_template = """\
from builtins import property as _property
from operator import itemgetter as _itemgetter
from collections import OrderedDict
from pyrsistent import v, plist
class {typename}(object):
    '{typename}({arg_list})'
    __slots__ = ('__mochi_v')
    _fields = {field_names!r}
    def __new__(_cls, {arg_list}):
        return object.__new__(_cls)
    def __init__(self, {arg_list}):
        self.__mochi_v = v({arg_list})
    def __repr__(self):
        return self.__class__.__name__ + '({repr_fmt})' % tuple(self.__mochi_v)
    @property
    def __dict__(self):
        return OrderedDict(zip(self._fields, self.__mochi_v))
    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values.'
        return self.__dict__
    def __getnewargs__(self):
        return tuple(self)
    def __getstate__(self):
        'Exclude the OrderedDict from pickling'
        return None
    def __getitem__(self, *args, **kwargs):
        return self.__mochi_v.__getitem__(*args, **kwargs)
    def __len__(self, *args, **kwargs):
        return self.__mochi_v.__len__(*args, **kwargs)
    def __getslice__(self, *args, **kwargs):
        return self.__mochi_v.__getslice__(*args, **kwargs)
    def __iter__(self, *args, **kwargs):
        return self.__mochi_v.__iter__(*args, **kwargs)
    def set(self, *args, **kwargs):

        return self.__mochi_v.set(*args, **kwargs)
    def mset(self, *args, **kwargs):
        return self.__mochi_v.mset(*args, **kwargs)
    def tolist(self, *args, **kwargs):
        return plist(self.__mochi_v)

{field_defs}
"""

_repr_template = '{name}=%r'

_field_template = '''\
    {name} = _property(_itemgetter({index:d}), doc='Alias for field number {index:d}')
'''

def namedtuple(typename, field_names, verbose=False, rename=False):
    """Returns a new subclass of tuple with named fields.
    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessable by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)
    """

    # Validate the field names.  At the user's option, either generate an error
    # message or automatically replace the field name with a valid name.
    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    field_names = list(map(str, field_names))
    typename = str(typename)
    if rename:
        seen = set()
        for index, name in enumerate(field_names):
            if (not name.isidentifier()
                or _iskeyword(name)
                or name.startswith('_')
                or name in seen):
                field_names[index] = '_%d' % index
            seen.add(name)
    for name in [typename] + field_names:
        if type(name) != str:
            raise TypeError('Type names and field names must be strings')
        if not name.isidentifier():
            raise ValueError('Type names and field names must be valid '
                             'identifiers: %r' % name)
        if _iskeyword(name):
            raise ValueError('Type names and field names cannot be a '
                             'keyword: %r' % name)
    seen = set()
    for name in field_names:
        if name.startswith('_') and not rename:
            raise ValueError('Field names cannot start with an underscore: '
                             '%r' % name)
        if name in seen:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen.add(name)

    # Fill-in the class template
    class_definition = _class_template.format(
        typename = typename,
        field_names = tuple(field_names),
        num_fields = len(field_names),
        arg_list = repr(tuple(field_names)).replace("'", "")[1:-1],
        repr_fmt = ', '.join(_repr_template.format(name=name)
                             for name in field_names),
        field_defs = '\n'.join(_field_template.format(index=index, name=name)
                               for index, name in enumerate(field_names)),
    )

    # Execute the template string in a temporary namespace and support
    # tracing utilities by setting a value for frame.f_globals['__name__']
    namespace = dict(__name__='namedpvector_%s' % typename)
    exec(class_definition, namespace)
    result = namespace[typename]
    result._source = class_definition
    if verbose:
        print(result._source)

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in environments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try:
        result.__module__ = _sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return result


def pclass(members='', name='PClass', verbose=False):
    """
    Produces a class that either can be used standalone or as a base class for persistent classes.
    This is a thin wrapper around a named tuple.
    Constructing a type and using it to instantiate objects:
    >>> Point = pclass('x, y', name='Point')
    >>> p = Point(1, 2)
    >>> p2 = p.set(x=3)
    >>> p
    Point(x=1, y=2)
    >>> p2
    Point(x=3, y=2)
    Inheriting from a constructed type. In this case no type name needs to be supplied:
    >>> class PositivePoint(pclass('x, y')):
    ...     __slots__ = tuple()
    ...     def __new__(cls, x, y):
    ...         if x > 0 and y > 0:
    ...             return super(PositivePoint, cls).__new__(cls, x, y)
    ...         raise Exception('Coordinates must be positive!')
    ...
    >>> p = PositivePoint(1, 2)
    >>> p.set(x=3)
    PositivePoint(x=3, y=2)
    >>> p.set(y=-3)
    Traceback (most recent call last):
    Exception: Coordinates must be positive!
    The persistent class also supports the notion of frozen members. The value of a frozen member
    cannot be updated. For example it could be used to implement an ID that should remain the same
    over time. A frozen member is denoted by a trailing underscore.
    >>> Point = pclass('x, y, id_', name='Point')
    >>> p = Point(1, 2, id_=17)
    >>> p.set(x=3)
    Point(x=3, y=2, id_=17)
    >>> p.set(id_=18)
    Traceback (most recent call last):
    AttributeError: Cannot set frozen members id_
    """

    if isinstance(members, six.string_types):
        members = members.replace(',', ' ').split()

    def frozen_member_test():
        frozen_members = ["'%s'" % f for f in members if f.endswith('_')]
        if frozen_members:
            return """
        frozen_fields = fields_to_modify & set([{frozen_members}])
        if frozen_fields:
            raise AttributeError('Cannot set frozen members %s' % ', '.join(frozen_fields))
            """.format(frozen_members=', '.join(frozen_members))

        return ''

    quoted_members = ', '.join("'%s'" % m for m in members)
    template = """
class {class_name}(namedtuple('PClassBase', [{quoted_members}], verbose={verbose})):
    __slots__ = tuple()
    def __repr__(self):
        return super({class_name}, self).__repr__().replace('PClassBase', self.__class__.__name__)
    def set(self, **kwargs):
        if not kwargs:
            return self
        fields_to_modify = set(kwargs.keys())
        if not fields_to_modify <= {member_set}:
            raise AttributeError("'%s' is not a member" % ', '.join(fields_to_modify - {member_set}))
        {frozen_member_test}
        return self.__class__.__new__(self.__class__, *map(kwargs.pop, [{quoted_members}], self))
""".format(quoted_members=quoted_members,
               member_set="set([%s])" % quoted_members if quoted_members else 'set()',
               frozen_member_test=frozen_member_test(),
               verbose=verbose,
               class_name=name)

    if verbose:
        print(template)

    from collections import namedtuple
    namespace = dict(namedtuple=namedtuple, __name__='pyrsistent_pclass')
    try:
        six.exec_(template, namespace)
    except SyntaxError as e:
        raise SyntaxError(e.message + ':\n' + template)

    return namespace[name]