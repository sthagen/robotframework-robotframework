#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import warnings
from collections.abc import Iterable, Mapping
from collections import UserString
from io import IOBase
from os import PathLike
from typing import get_args, get_origin, Literal, TypedDict, Union
try:
    from types import UnionType
except ImportError:    # Python < 3.10
    UnionType = ()

try:
    from typing_extensions import TypedDict as ExtTypedDict
except ImportError:
    ExtTypedDict = None


TRUE_STRINGS = {'TRUE', 'YES', 'ON', '1'}
FALSE_STRINGS = {'FALSE', 'NO', 'OFF', '0', 'NONE', ''}
typeddict_types = (type(TypedDict('Dummy', {})),)
if ExtTypedDict:
    typeddict_types += (type(ExtTypedDict('Dummy', {})),)


def is_integer(item):
    return isinstance(item, int)


def is_number(item):
    return isinstance(item, (int, float))


def is_bytes(item):
    return isinstance(item, (bytes, bytearray))


def is_string(item):
    return isinstance(item, str)


def is_pathlike(item):
    return isinstance(item, PathLike)


def is_list_like(item):
    if isinstance(item, (str, bytes, bytearray, UserString, IOBase)):
        return False
    return isinstance(item, Iterable)


def is_dict_like(item):
    return isinstance(item, Mapping)


def is_union(item):
    return isinstance(item, UnionType) or get_origin(item) is Union


def type_name(item, capitalize=False):
    """Return "non-technical" type name for objects and types.

    For example, 'integer' instead of 'int' and 'file' instead of 'TextIOWrapper'.
    """
    if is_union(item):
        return 'Union'
    origin = get_origin(item)
    if origin:
        item = origin
    if hasattr(item, '_name') and item._name:
        # Prior to Python 3.10, Union, Any, etc. from typing didn't have `__name__`.
        # but instead had `_name`. Python 3.10 has both and newer only `__name__`.
        # Also, pandas.Series has `_name` but it's None.
        name = item._name
    elif isinstance(item, IOBase):
        name = 'file'
    else:
        typ = type(item) if not isinstance(item, type) else item
        named_types = {str: 'string', bool: 'boolean', int: 'integer',
                       type(None): 'None', dict: 'dictionary'}
        name = named_types.get(typ, typ.__name__.strip('_'))
    return name.capitalize() if capitalize and name.islower() else name


def type_repr(typ, nested=True):
    """Return string representation for types.

    Aims to look as much as the source code as possible. For example, 'List[Any]'
    instead of 'typing.List[typing.Any]'.
    """
    if typ is type(None):
        return 'None'
    if typ is Ellipsis:
        return '...'
    if is_union(typ):
        return ' | '.join(type_repr(a) for a in get_args(typ)) if nested else 'Union'
    if get_origin(typ) is Literal:
        if nested:
            args = ', '.join(repr(a) for a in get_args(typ))
            return f'Literal[{args}]'
        return 'Literal'
    name = _get_type_name(typ)
    if nested:
        args = ', '.join(type_repr(a) for a in get_args(typ))
        if args:
            return f'{name}[{args}]'
    return name


def _get_type_name(typ):
    # See comment in `type_name` for explanation about `_name`.
    for attr in '__name__', '_name':
        name = getattr(typ, attr, None)
        if name:
            return name
    return str(typ)


# TODO: Remove has_args in RF 8.
def has_args(type):
    """Helper to check has type valid ``__args__``.

    Deprecated in Robot Framework 7.3 and will be removed in Robot Framework 8.0.
    ``typing.get_args`` can be used instead.
    """
    warnings.warn("'robot.utils.has_args' is deprecated and will be removed in "
                  "Robot Framework 8.0. Use 'typing.get_args' instead.")
    return bool(get_args(type))


def is_truthy(item):
    """Returns `True` or `False` depending on is the item considered true or not.

    Validation rules:

    - If the value is a string, it is considered false if it is `'FALSE'`,
      `'NO'`, `'OFF'`, `'0'`, `'NONE'` or `''`, case-insensitively.
    - Other strings are considered true.
    - Other values are handled by using the standard `bool()` function.

    Designed to be used also by external test libraries that want to handle
    Boolean values similarly as Robot Framework itself. See also
    :func:`is_falsy`.
    """
    if isinstance(item, str):
        return item.upper() not in FALSE_STRINGS
    return bool(item)


def is_falsy(item):
    """Opposite of :func:`is_truthy`."""
    return not is_truthy(item)
