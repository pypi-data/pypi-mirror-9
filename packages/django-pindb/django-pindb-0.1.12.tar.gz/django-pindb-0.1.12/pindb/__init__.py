from __future__ import absolute_import

__version__ = (0, 1, 12)  # remember to change setup.py

import contextlib
from functools import wraps
from threading import local
from itertools import cycle
from random import randint
from warnings import warn

from django.conf import settings
from django.utils import importlib

from .exceptions import PinDbException, PinDbConfigError, UnpinnedWriteException

__all__ = (
    'PinDbException', 'PinDbConfigError', 'UnpinnedWriteException',
    'unpin_all', 'pin', 'get_pinned', 'get_newly_pinned',
    'is_pinned', 'get_replica', 'unpinned_replica',
    'populate_replicas', 'StrictPinDbRouter', 'GreedyPinDbRouter'
)

_locals = local()

def is_enabled():
    return getattr(settings, 'PINDB_ENABLED', True)

def unpin_all():
    """Clear the new and old pinnings and the chosen replicas."""
    # the authoritative set of pinned aliases:
    _locals.pinned_set = set()
    # the newly-pinned ones for advising the pinned context (i.e. for persistence):
    _locals.newly_pinned_set = set()
    # replica choices already made during this pinning context:
    _locals.chosen_replicas = {}  # {master alias: replica alias}

# Number of replicas for each DB set, loaded when the Router is constructed;
# zero-based to ease using random.randint. If a set as 3 replicas, there will
# be a 2 here.
DB_SET_SIZES = {}  # How many slaves each DB set has - 1
def _init_state():
    if getattr(_locals, 'inited', False):
        return
    unpin_all()
    _locals.inited = True

def pin(alias, count_as_new=True):
    _init_state()
    _locals.pinned_set.add(alias)
    if count_as_new:
        _locals.newly_pinned_set.add(alias)

def _unpin_one(alias, also_unpin_new=True):
    """
    Not intended for external use; just here for the decorators below.
    """
    _init_state()
    _locals.pinned_set.remove(alias)
    if also_unpin_new:
        _locals.newly_pinned_set.discard(alias)

def get_pinned():
    _init_state()
    return _locals.pinned_set.copy()

def get_newly_pinned():
    _init_state()
    return _locals.newly_pinned_set.copy()

def is_pinned(alias):
    _init_state()
    return alias in _locals.pinned_set

def is_newly_pinned(alias):
    _init_state()
    return alias in _locals.newly_pinned_set

REPLICA_TEMPLATE = "%s-%s"
def _make_replica_alias(master_alias, replica_num):
    return REPLICA_TEMPLATE % (master_alias, replica_num)

def get_replica(master_alias):
    """Return an arbitrary replica of a given master.

    If one was already chosen during this pinning context, keep returning the
    same one.

    """
    _init_state()
    try:
        effective_size = DB_SET_SIZES[master_alias]
    except KeyError:
        # this happens if the main router isn't a PinDB router.
        #  in that case, we're meant to be disabled;
        #  just return master_alias as it's the best we can do.
        return master_alias
    if effective_size == -1:
        return master_alias
    else:
        previous_replica = _locals.chosen_replicas.get(master_alias)
        if previous_replica:
            return previous_replica
        replica_num = randint(0, effective_size)

        chosen_replica = _make_replica_alias(master_alias, replica_num)
        _locals.chosen_replicas[master_alias] = chosen_replica

        return chosen_replica

class unpinned_replica(object):
    """
    with unpinned_replica("default"):
        ...

    Read from a replica despite pinning state.
    """
    def __init__(self, alias):
        self.alias = alias

    def __enter__(self):
        self.was_pinned = is_pinned(self.alias)
        self.was_newly_pinned = is_newly_pinned(self.alias)
        if self.was_pinned:
            _unpin_one(self.alias, True)

    def __exit__(self, type, value, tb):
        if self.was_pinned:
            pin(self.alias, self.was_newly_pinned)

        if any((type, value, tb)):
            raise type, value, tb

def _mash_aliases(aliases):
    if not isinstance(aliases, basestring) and hasattr(aliases, '__iter__'):
        aliases = set(aliases)
    else:
        aliases = set([aliases])
    return aliases

def with_replicas(aliases):
    """
    @with_replicas([alias,...])
    def func...

    Read from replicas despite pinning state.
    """
    aliases = _mash_aliases(aliases)
    # FIXME: test this.
    def make_wrapper(func):
        replicas = [unpinned_replica(alias) for alias in aliases]
        @wraps(func)
        def wrapper(*args, **kwargs):
            with contextlib.nested(*replicas):
                return func(*args, **kwargs)
        return wrapper
    return make_wrapper

class master(object):
    """Context manager for temporarily writing to a master DB

    While active, any writes to the given DB set will go to the set's master,
    regardless of pinning state. Pinning state is not changed by this. ::

        with master("default"):
            ...

    """
    # TODO: make this optionally take a list of models for which to pin appropriately.
    def __init__(self, alias):
        self.alias = alias
        _init_state()

    def __enter__(self):
        self.was_pinned = is_pinned(self.alias)
        self.was_newly_pinned = is_newly_pinned(self.alias)
        pin(self.alias, False)

    def __exit__(self, type, value, tb):
        if not self.was_pinned:
            _unpin_one(self.alias, False)
        if not self.was_newly_pinned:
            # FIXME: should be abstracted somewhere, whoops.
            _locals.newly_pinned_set.discard(self.alias)

        if any((type, value, tb)):
            raise type, value, tb

def with_masters(aliases):
    """
    @with_masters([alias,...])
    def func...

    Write to masters despite (and without affecting) pinning state.
    """
    aliases = _mash_aliases(aliases)
    # FIXME: test this.
    def make_wrapper(func):
        masters = [master(alias) for alias in aliases]
        @wraps(func)
        def wrapper(*args, **kwargs):
            with contextlib.nested(*masters):
                return func(*args, **kwargs)
        return wrapper
    return make_wrapper

# TODO: add logging to aid debugging client code.
def populate_replicas(masters, replicas_overrides, unmanaged_default=False):
    if not 'default' in masters and not unmanaged_default:
        raise PinDbConfigError("You must declare a default master.")

    ret = {}
    for alias, master_values in masters.items():
        ret[alias] = master_values
        try:
            replica_overrides = replicas_overrides[alias]
        except KeyError:
            raise PinDbConfigError("No replica settings found for DB set %s" % alias)
        for i, replica_override in enumerate(replica_overrides):
            replica_alias = _make_replica_alias(alias, i)
            replica_settings = master_values.copy()
            replica_settings.update(replica_override)
            replica_settings['TEST_MIRROR'] = alias
            ret[replica_alias] = replica_settings

    return ret

class DummyRouter(object):
    def db_for_read(self, model, **hints):
        return "default"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(slef, db, model):
        return True

class PinDbRouterBase(object):
    def __init__(self):
        if (not hasattr(settings, 'MASTER_DATABASES') or
            not hasattr(settings, 'DATABASE_SETS')):
            raise PinDbConfigError("You must define MASTER_DATABASES and DATABASE_SETS settings.")

        # stash the # to chose from to reduce per-call overhead in the routing.
        for alias, master_values in settings.MASTER_DATABASES.items():
            DB_SET_SIZES[alias] = len(settings.DATABASE_SETS[alias]) - 1
            if DB_SET_SIZES[alias] == -1:
                warn("No replicas found for %s; using just the master" % alias)

        # defer master selection to a domain-specific router.
        delegates = getattr(settings, 'PINDB_DELEGATE_ROUTERS', [])
        if delegates:
            from django.db.utils import ConnectionRouter
            self.delegate = ConnectionRouter(delegates)
        else:
            warn("Unable to load delegate router from settings.PINDB_DELEGATE_ROUTERS; using default and its replicas")
            # or just always use default's set.
            self.delegate = DummyRouter()

    def db_for_read(self, model, **hints):
        master_alias = self.delegate.db_for_read(model, **hints)
        if master_alias is None:
            master_alias = "default"

        if not is_enabled():
            return master_alias

        # allow anything unmanaged by the DB set system to work unhindered.
        if not master_alias in settings.MASTER_DATABASES:
            return master_alias

        if is_pinned(master_alias):
            return master_alias
        return get_replica(master_alias)

    def db_for_write(self, model, **hints):
        master_alias = self.delegate.db_for_write(model, **hints)
        if master_alias is None:
            master_alias = "default"

        if not is_enabled():
            return master_alias

        # allow anything unmanaged by the DB set system to work unhindered.
        if not master_alias in settings.MASTER_DATABASES:
            return master_alias
        return self._for_write_with_policy(master_alias, model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        return self.delegate.allow_relation(obj1, obj2, **hints)

    def allow_syncdb(self, db, model):
        return self.delegate.allow_syncdb(db, model)

class StrictPinDbRouter(PinDbRouterBase):
    def _for_write_with_policy(self, master_alias, model, **hints):
        if not is_pinned(master_alias):
            raise UnpinnedWriteException("Writes to %s aren't allowed because reads aren't pinned to it." % master_alias)
        return master_alias

class GreedyPinDbRouter(PinDbRouterBase):
    def _for_write_with_policy(self, master_alias, model, **hints):
        pin(master_alias)
        return master_alias
