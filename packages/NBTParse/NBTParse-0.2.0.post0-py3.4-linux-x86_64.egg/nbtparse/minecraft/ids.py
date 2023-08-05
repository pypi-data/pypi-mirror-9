"""Module for looking up blocks, items, entities, etc. by name or number.

Lookups are performed via :obj:`all_ids`; the rest of the section documents
the objects returned by it and how to manage the available namespaces.

"""

import abc
import collections
import collections.abc as cabc
import copy
import functools
import importlib
import io
import json
import logging
import numbers
import pathlib
import pkgutil
import sys

from ..semantics import nbtobject
from ..syntax import tags
from .. import exceptions


logger = logging.getLogger(__name__)


TYPE = 'type'
ITEM = 'item'
BLOCK = 'block'
ENTITY = 'entity'
#: The different types of identifiers allowed
ALLOWED_TYPES = frozenset((ITEM, BLOCK, ENTITY))

MAX_STACK = 64


class Named:
    """Root of the ID hierarchy; all IDs have names."""
    def __init__(self, *args, name=None, **kwargs):
        self._name = name
        super().__init__(*args, **kwargs)

    @property
    def name(self):
        """The name of this ID, or None if no name was specified.

        Named objects are renamed when placed into a namespace.

        """
        return self._name

    def rename(self, new_name: str) -> 'Named':
        """Duplicate this named object with a different name."""
        if new_name == self.name:
            return self
        result = copy.copy(self)
        result._name = new_name
        return result


class ClassID(Named, metaclass=abc.ABCMeta):
    """Abstract class for IDs which identify NBT objects."""
    @abc.abstractmethod
    def resolve_class(self) -> nbtobject.NBTMeta:
        """Returns a subclass of NBTObject.

        The subclass is suitable for objects with this ID.  This may involve
        importing the class from another module if it is not already imported.

        """
        raise NotImplementedError('ClassID does not implement resolve_class')


class ItemID(ClassID):
    """Information about an item ID."""
    def __init__(self, *, name: str=None, max_stack: int=MAX_STACK):
        super().__init__(name=name)
        self._max_stack = max_stack if max_stack is not None else MAX_STACK

    @property
    def max_stack(self) -> int:
        """How large stacks of this item may get."""
        return self._max_stack
    
    @property
    def type(self) -> str:
        """Always equal to 'item'."""
        return ITEM

    def __repr__(self) -> str:
        return 'ItemID(name={!r}, max_stack={!r})'.format(self.name,
                                                          self.max_stack)

    def resolve_class(self) ->nbtobject.NBTMeta:
        """Return :class:`~.item.Item`."""
        from . import item
        return item.Item


class BlockID(Named):
    """Information about a block ID."""
    def __init__(self, *, name: str=None, block_number: int=None,
                 item_id: ItemID, light: int=0, transparent: bool=False,
                 opacity: int=None, physics: bool=False):
        super().__init__(name=name)
        self._block_number = block_number
        self._item_id = item_id
        self._light = light if light is not None else 0
        self._transparent = transparent if transparent is not None else False
        self._opacity = opacity
        self._physics = physics if physics is not None else False

    def __repr__(self):
        return ('BlockID(name={!r}, block_number={!r}, item_id={!r}, '
                'light={!r}, transparent={!r}, opacity={!r}, physics={!r})'
                .format(self.name, self.block_number, self.item_id,
                        self.light, self.transparent, self.opacity,
                        self.physics))

    @property
    def type(self) -> str:
        """Always equal to 'block'."""
        return BLOCK

    @property
    def block_number(self):
        """The number used internally when storing this block in terrain."""
        return self._block_number

    @property
    def item_id(self):
        """The :class:`ItemID` for the item version of this block."""
        return self._item_id

    @property
    def light(self):
        """The amount of light this block emits."""
        return self._light

    @property
    def transparent(self):
        """Whether this block is transparent."""
        return self._transparent

    @property
    def opacity(self):
        """The amount of light this block impedes.

        None if :attr:`transparent` is False.

        """
        return self._opacity

    @property
    def physics(self):
        """True if this block falls by itself."""
        return self._physics

    def renumber(self, new_id: str) -> 'BlockID':
        """Duplicate this block ID with a different number"""
        if new_id == self._block_number:
            return self
        result = copy.copy(self)
        result._block_number = new_id
        return result


class EntityID(ClassID):
    """Information about a (tile) entity ID."""
    def __init__(self, class_name: str):
        self._name = None
        self._class_name = class_name

    @property
    def type(self):
        """Always equal to 'entity'."""
        return ENTITY

    @property
    def class_name(self):
        """The fully-qualified name of this (tile) entity's class.

        Formatted as follows::

            some.module.name:SomeClassName

        """
        return self._class_name

    def resolve_class(self) -> nbtobject.NBTMeta:
        """Returns the class used to create instances of this (tile) entity.

        This may involve importing the class.

        """
        module_name, class_name = self._class_name.split(':')
        result = importlib.import_module(module_name)
        for part in class_name.split('.'):
            result = getattr(result, part)
        return result


class Namespace(cabc.Mapping):
    """A Minecraft namespace.

    Namespaces associate block names and numbers with each other, and
    store additional information about blocks, items, and entities.

    A namespace maps names and numbers to instances of the various FooID
    classes defined in the ids module.  Iterating over a namespace will only
    produce the names, since every numbered block also has a name.

    """
    def __init__(self, contents: {str: Named}, numericals: {int: str}):
        contents = dict(contents)
        numericals = dict(numericals)
        reversed_numericals = {v: k for k, v in numericals.items()}
        if not contents.keys() >= set(numericals.values()):
            raise ValueError('numericals.values() should be a subset of '
                             'contents.keys()')
        if len(numericals) != len(reversed_numericals):
            raise ValueError('numericals.values() must not contain '
                             'duplicates.')
        self._numericals = numericals

        self._contents = {}
        for name, identifier in contents.items():
            identifier = identifier.rename(name)
            if name in reversed_numericals:
                number = reversed_numericals[name]
                try:
                    identifier = identifier.renumber(number)
                except AttributeError as exc:
                    raise ValueError('Each numerical must refer to a block ID'
                                     ) from exc
            self._contents[name] = identifier

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            name = self._numericals[int(key)]
        else:
            name = key
        return self._contents[name]

    def __iter__(self):
        return iter(self._contents)

    def __len__(self):
        return len(self._contents)

    def __repr__(self):
        return '<Namespace: {!r} names>'.format(len(self))


#: The name of the "standard" namespace, containing ID's used by vanilla
#: Minecraft
STANDARD_NAMESPACE_NAME = 'minecraft'



def _inflate(deflated: dict) -> Named:
    """Transform JSON output into an Identifier."""
    if deflated is None:
        return None
    try:
        typestr = deflated['type']
    except KeyError as exc:
        raise exceptions.ParserError() from exc
    if typestr == BLOCK:
        result = BlockID(block_number=deflated.get('id'),
                         transparent=deflated.get('transparent'),
                         light=deflated.get('light'),
                         opacity=deflated.get('opacity'),
                         physics=deflated.get('physics'),
                         item_id=_inflate(deflated.get('item_identifier')),
                         )
    elif typestr == ITEM:
        result = ItemID(max_stack=deflated.get('max_stack'))
    elif typestr == ENTITY:
        result = EntityID(class_name=deflated.get('class_name'))
    else:
        raise exceptions.ParserError('Unknown type {!r}'.format(typestr))
    return result


def read_config(infile: io.TextIOBase) -> Namespace:
    """Read a configuration file and produce a namespace dictionary.

    Return a suitable argument to :func:`register_namespace`.

    Config file format is simple JSON, encoded in UTF-8::

        {
            "stone": {
                "id": 1,
                "item_identifier": {
                    "id": 1,
                    "item_identifier": null,
                    "max_stack": 64,
                    "type": "item"
                }
                "light": 0,
                "opacity": null,
                "transparent": false,
                "type": "block"
            }
        }

    Null values may be omitted, except that id and type are mandatory and
    must not be null.

    If the above format is not followed or the file is invalid JSON, a
    :exc:`~.exceptions.ParserError` is raised.

    """
    try:
        raw_ns = json.load(infile)
    except ValueError as exc:
        raise exceptions.ParserError() from exc
    contents = {name: _inflate(value) for name, value in raw_ns.items()}
    numericals = {ident.block_number: name for name, ident in contents.items()
                  if hasattr(ident, 'block_number')}
    return Namespace(contents, numericals)


@functools.singledispatch
def _deflate(ident: Named) -> dict:
    """Transform argument into something suitable for JSON encoding."""
    raise TypeError('Expected some kind of identifier but got {}'
                    .format(type(ident).__name__))


@_deflate.register(BlockID)
def _(ident: BlockID) -> dict:
    result = {TYPE: BLOCK}
    # XXX: Do not change these to if ident.foo; some are integers which
    #      might be zero, or coerce to integers
    if ident.block_number is not None:
        result['id'] = ident.block_number
    if ident.transparent is not None:
        result['transparent'] = ident.transparent
    if ident.light is not None:
        result['light'] = ident.light
    if ident.opacity is not None:
        result['opacity'] = ident.opacity
    if ident.item_id is not None:
        result['item_identifier'] = _deflate(ident.item_id)
    return result


@_deflate.register(ItemID)
def _(ident: ItemID) -> dict:
    result = {TYPE: ITEM}
    if ident.max_stack is not None:
        result['max_stack'] = ident.max_stack
    return result


@_deflate.register(EntityID)
def _(ident: EntityID) -> dict:
    result = {TYPE: ENTITY}
    if ident.class_name is not None:
        result['class_name'] = ident.class_name
    return result


def write_config(outfile: io.TextIOBase, namespace: Namespace, *,
                 pprint=False):
    """Write a configuration file.

    Use a format suitable for :func:`read_config`.  Nulls are omitted.

    """
    result = {name: _deflate(indent) for name, indent in namespace.items()}
    if pprint:
        indent = '\t'
        separators = (',', ': ')
        sort_keys = True
    else:
        indent = None
        separators = (',', ':')
        sort_keys = False
    json.dump(result, outfile, indent=indent, separators=separators,
              sort_keys=sort_keys)
    outfile.write('\n')


STANDARD_CONFIG_FILENAME = 'standard.json'
_namespaces = collections.OrderedDict()


def register_namespace(name: str, namespace: Namespace):
    """Register a new namespace of ID's.

    You may register a new version of the standard namespace
    (``'minecraft'``).  Doing so will "hide" the official version.  You
    can always unregister your custom version later, and the official
    version will be automatically re-registered.

    """
    _namespaces[name] = namespace
    _namespaces.move_to_end(name)


def get_namespace(name: str) -> Namespace:
    """Produce the block namespace with the given name.

    Namespaces are immutable, so you should not use this mechanism to
    alter a namespace in-place.  Instead, re-register the modified version
    of the namespace with :func:`register_namespace`.

    Raises a :exc:`KeyError` if no such namespace exists.

    """
    return _namespaces[name]


def unregister_namespace(name: str):
    """Remove the given namespace, preventing lookups.

    Attempting to unregister the standard namespace (i.e. ``'minecraft'``)
    will automatically re-register the "default" version of the standard
    namespace.

    """
    del _namespaces[name]
    if name == STANDARD_NAMESPACE_NAME:
        if STANDARD_NAMESPACE is None:
            logger.error('Unable to re-register standard namespace '
                         '(not available)')
        else:
            register_namespace(STANDARD_NAMESPACE_NAME,
                               STANDARD_NAMESPACE)


_config_data = pkgutil.get_data(__name__, STANDARD_CONFIG_FILENAME)
if _config_data is not None:
    _config_data = _config_data.decode('utf8')
    STANDARD_NAMESPACE = read_config(io.StringIO(_config_data))
    register_namespace(STANDARD_NAMESPACE_NAME, STANDARD_NAMESPACE)
else:
    logger.error('Standard namespace not available')
    STANDARD_NAMESPACE = None


class _MetaNamespace(cabc.Mapping):
    """The class of the all_ids object."""
    def __getitem__(self, key: str) -> Named:
        if type(key) is str:
            try:
                namespace, identifier = key.split(':', maxsplit=1)
            except ValueError:
                namespace = None
                identifier = key
            try:
                identifier = int(identifier)
            except ValueError:
                pass
        elif type(key) is int:
            namespace = None
            identifier = key
        else:
            raise KeyError(key)
        if namespace is None:
            for namespace in reversed(_namespaces):
                contents = _namespaces[namespace]
                if identifier in contents:
                    return contents[identifier]
            else:
                raise KeyError(key)
        else:
            return _namespaces[namespace][identifier]

    def __iter__(self):
        for name, space in _namespaces.items():
            for identifier in space:
                yield '{}:{}'.format(name, identifier)

    def __len__(self):
        return sum(len(namespace) for namespace in _namespaces.values())

    def __repr__(self):
        return '<all_ids: mapping from strings to identifiers>'


def main():
    """Run this module as a script."""
    import argparse
    ids = sys.modules[__name__]
    parser = argparse.ArgumentParser(description='Look up a block or item'
                                     'ID')
    parser.add_argument('identifier', help='The block number or item ID '
                        'to look up, optionally with a namespace prefix '
                        '(e.g. minecraft:stone)', type=str)
    parser.add_argument('-N', '--namespace', nargs=2,
                        help='Register an additional namespace before '
                        'doing the lookup; may be specified multiple '
                        'times', action='append',
                        metavar=('name', 'file'))
    parser.add_argument('-i', '--force-item', help='Look up an item ID; '
                        'convert block IDs to item IDs if necessary.',
                        action='store_true')
    args = parser.parse_args()
    if args.namespace is not None:
        for item in args.namespace:
            name, file = item
            contents = read_config(file)
            Module.register_namespace(name, contents)
    try:
        identifier = ids.all_ids[args.identifier]
    except KeyError:
        sys.exit('{} is not a valid identifier'
                    .format(args.identifier))
    if args.force_item and identifier.type == BLOCK:
        identifier = identifier.item_id
    if identifier.type == BLOCK:
        print('{} is block number {}'.format(args.identifier,
                                                identifier.block_number))
        print('{} is named {}'.format(args.identifier, identifier.name))
    else:
        print('{} is of type {}'.format(args.identifier, identifier.type))
    if identifier.type == BLOCK:
        if identifier.transparent:
            print('It is transparent with an opacity of {}'
                .format(identifier.opacity))
        if identifier.light != 0:
            print('It produces a light level of {}'
                .format(identifier.light))
        if identifier.physics:
            print('It falls if unsupported')
    elif identifier.type == ITEM:
        if identifier.max_stack != 1:
            print('It is stackable up to {} '
                'items'.format(identifier.max_stack))
    elif identifier.type == ENTITY:
        print('It is handled by class {}'.format(identifier.class_name))


all_ids = _MetaNamespace()
"""Mapping from 'namespace:identifier' strings to :class:`Named` objects.

The primary interface to the ids module.  Use like a dictionary::

    all_ids['minecraft:stone']

Indexing with a number produces the corresponding block::

    all_ids['minecraft:1']

Indexing without a namespace will search every registered namespace in reverse
order of registration (i.e. most recently registered first)::

    all_ids['stone']

Bare integers may also be looked up::

    all_ids[1]

"""


if __name__ == '__main__':
    main()
