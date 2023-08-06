import collections
import collections.abc as cabc
import logging
import types
import weakref

from .. import exceptions


logger = logging.getLogger(__name__)


class _ClassSpec:
    def __init__(self, target: 'entity.EntityMeta', ident: str):
        self._target = weakref.ref(target)
        hash(self._target)  # ensure hashability even if target dies
        self._ident = ident

    @property
    def target(self):
        return self._target()

    @property
    def ident(self):
        return self._ident

    def __hash__(self):
        return hash((type(self), self.ident))

    def __eq__(self, other):
        return (type(self) is type(other) and
                self.ident == other.ident)

    def __ne__(self, other):
        return not self == other


class EntityNamespace(cabc.Mapping):
    """A namespace of entities.  Maps identifier strings to classes.

    Class is a multiton; calling ``EntityNamespace('foo')`` always returns the
    same object.

    .. warning::

        If any of the registered classes cease to exist while iterating over a
        namespace, undefined behavior occurs.

    """
    __instances = {}
    def __new__(cls, name: str):
        try:
            return cls.__instances[name]
        except KeyError:
            result = super().__new__(cls)
            cls.__instances[name] = result
            result._initialized = False
            return result

    def __init__(self, name):
        # If __new__ returns the same object more than once, __init__ can be
        # called multiple times.  Guard against this.
        if self._initialized:
            return
        self._initialized = True
        self._name = name
        self._registered_modules = set()
        # items: module names
        self._staging_classes = collections.defaultdict(set)
        # keys: module names, values: sets of class specs (see below)
        self._enabled_classes = weakref.WeakValueDictionary()
        # keys: ident strings, values: classes

    @property
    def name(self):
        """The name of this namespace."""
        return self._name

    def __repr__(self):
        return 'EntityNamespace({!r})'.format(self.name)

    def register_class(self, class_: 'entity.EntityMeta', ident: str):
        """Register a class with this namespace.

        The class's module must also be separately registered using
        :meth:`register_module`.

        """
        logger.debug('Registering class %r', class_)
        module = class_.__module__
        if module in self._registered_modules:
            self._enabled_classes[ident] = class_
        else:
            self._staging_classes[module].add(_ClassSpec(class_, ident))

    def register_module(self, module: types.ModuleType):
        """Register a module with this namespace.

        This is a necessary step to use the module's entities.

        Registering an identifier which is already attached to the namespace
        will raise a :exc:`.exceptions.DuplicateIDError`, except that multiple
        registrations of the same class are legal and ignored.  This error is
        raised here rather than in :func:`register_class`.

        .. note::

            Modules should not attempt to register themselves, for this is an
            import-time side effect.  Instead, it is recommended to register
            modules in the top-level script (i.e. the ``__main__`` module).
            NBTParse automatically registers the built-in entity modules with
            the ``'minecraft'`` namespace when :mod:`nbtparse.minecraft` is
            imported, but this is not an appropriate model for external
            libraries because you cannot be sure your package will be imported
            early enough.  Instead, provide a function which the client
            application can call into.

        """
        logger.debug('Registering module %r', module)
        self._registered_modules.add(module.__name__)
        staging_set = self._staging_classes[module.__name__]
        del self._staging_classes[module.__name__]
        result = {}
        for class_spec in staging_set:
            target = class_spec.target
            if target is None:
                continue
            ident = class_spec.ident
            if ident in self:
                exc_class = exceptions.DuplicateIDError
                exc_msg = ("The ID {!r} already refers to {!r}, so it can't "
                           "refer to {!r}".format(ident,
                                                  self.get_class(ident),
                                                  target))
                raise exc_class(exc_msg)
            result[ident] = target
        self._enabled_classes.update(result)

    def __getitem__(self, key: str) -> 'entity.EntityMeta':
        return self._enabled_classes[key]

    def __iter__(self):
        return iter(self._enabled_classes)

    def __len__(self):
        return len(self._enabled_classes)


def register_class(ident: str, namespace: str='') -> callable:
    """Decorator to register a class with the entity IDs system.

    Usually called automatically from :class:`entity.EntityMeta`; you should
    not need to call this yourself.

    """
    def decorator(class_: 'entity.EntityMeta') -> 'entity.EntityMeta':
        EntityNamespace(namespace).register_class(class_, ident)
        return class_
    return decorator
