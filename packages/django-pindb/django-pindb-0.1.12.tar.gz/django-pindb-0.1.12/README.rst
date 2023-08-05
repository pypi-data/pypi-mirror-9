=====
pindb
=====

pindb is a master/slave router toolkit for Django.  It provides database replica pinning, round-robin read from replicas, the use of unmanaged databases side by side with managed ones, and delegate routers for deciding among sets of replicated DBs.

TL;DR API
=========

::

    # Try to save without pinning:
    foo = Model.objects.all()[0]
    
    # UnpinnedWriteException raised under strict mode, or master pinning occurs under greedy mode.         
    foo.save()
    
    # read only from the master, allow writes.
    pindb.pin(alias)
    
    # Initialize/end the container:
    pindb.unpin_all()
    
    with unpinned_replica(alias):
       ... # read from replicas despite pinning state
    # or 
    queryset.using(pindb.get_replica('master-alias'))
    
    with master(alias):
       ... # write to master despite pinning state

Jargon
======

Master refers to a writable DB.  Replica (or slave) refers to a read-only
DB whose data comes from master writes.  One or more master/slave database sets can help scale reads and avoid lock contention on the master.  
Typically all reads go to  replicas until a write occurs -- then all subsequent 
reads also go to the master to avoid inconsistent reads due to replication lag.  
Pinning is time-based and round-trips between web requests via cookies.  See 
"design notes" below for more.

Installation
============

::

    pip install pindb

TL;DR: 
 
#. Set ``DATABASES_ROUTERS`` to use a pindb router
#. set ``PINDB_ENABLED`` to False under test
#. Define DB masters and replica sets.
#. populate ``DATABASES`` with ``pindb.populate_replicas``.
#. Add ``PinDbMiddleware`` to your middleware.
#. Integrate with celery (if needed).
#. profile for places to explicitly side-step pinning.

More explicitly:

Add ``pindb.StrictPinDbRouter`` or ``pindb.GreedyPinDbRouter`` to
``DATABASE_ROUTERS``.

``StrictPinDbRouter`` requires that pinning be declared before a write is
attempted. The advantage is that read replicas are used as much as
possible. The disadvantage is that your code will need many declarations to
explicitly allow and opt out of pinning.

``GreedyPinDbRouter`` will pin to a master as soon as a write occurs. The
advantage is that most of your code will just work. The disadvantage is
that you will use the read replicas less than possible. You also might
encounter more situations where the state of your DB changes behind your
back: you might read from a lagged replica, then perform a write (which
pins you to the master) based on that old information.

``PINDB_ENABLED`` can be used to disable pindb under 
test.  Each TEST_MIRROR'd alias gets its own connection (and hence transaction), 
which is problematic under Django's `TestCase`_, where a master write will not 
be visible under the replica's connection. 

pindb has an extensive test suite;
disabling it under your own test suite is sane/recommended.

.. _`TestCase`: https://docs.djangoproject.com/en/1.4/topics/testing/#testcase

If you need to manage more than 1 master/replica set, add
``PINDB_DELEGATE_ROUTERS`` for pindb to defer to on DB set selection. This is
just another Django `database router`_ which should return a master alias; 
pindb will then choose a master or replica as appropriate for the current pinning
state of the returned master.

.. _`database router`: https://docs.djangoproject.com/en/1.4/topics/db/multi-db/#database-routers

Define ``MASTER_DATABASES``, same schema as ``DATABASES``::

    DATABASES = {
      "unmanaged": {
        # HOST0, etc.
      }
    }

    MASTER_DATABASES = {
      "default": {
        # HOST1, etc.
      },
      "some_other_master": {
        ...
      }
    }

Define ``DATABASE_SETS``, which overrides specific settings for replicas::

    DATABASE_SETS = {
      "default": [{HOST:HOST1}, {HOST:HOST2}, ...],
      "some_other_master": [...] # zero or more replicas is fine.
    }

Finalize ``DATABASES`` with ``pindb.populate_replicas``::

    DATABASES.update(populate_replicas(MASTER_DATABASES, DATABASE_SETS))

Add ``pindb.middleware.PinDbMiddleware`` to your ``MIDDLEWARE_CLASSES``
before any expected database access.

Optionally, throughout your codebase, if you intend to write, declare it 
as early as possible to avoid inconsistent reads off the related replicas::

    pin("default")

That will cause all future reads to use the master.

To use under celery, hook ``celery.signals.task_postrun`` to call
``pindb.unpin_all``::

    import pindb
    from celery.signals import task_postrun

    def end_pinning(**kwargs):
      pindb.unpin_all()
    task_postrun.connect(end_pinning)

Exceptions and avoiding them
============================

Exceptions
----------

``PinDbConfigError`` may be caused by...

* Your settings not including ``MASTER_DATABASES`` and ``DATABASE_SETS``
* Your ``MASTER_DATABASES`` not including a "default" and populate_replicas
  being called without passing ``unmanaged_default=True``.
* Declaring an alias in ``MASTER_DATABASES`` which does not have a related
  ``DATABASE_SETS`` entry

``UnpinnedWriteException`` may be caused by...

* ``Model.objects.create``, ``Model.save``, ``qs.update``, or ``qs.delete``
  without previously calling ``pindb.pin`` for the master

  Note that writes to unmanaged aliases (that is, ones unlisted in
  ``MASTER_DATABASES`` and related ``DATABASE_SETS``) are allowed at any time.

Overriding pinning
------------------

If you wish to read from a replica despite having previously pinned the master,
you can do so with... ::

    with pindb.unpinned_replica(alias):
      # code which reads from replicas

If you wish to write to a master despite not having pinned to it, you can do so
with... ::

    with pindb.master(alias):
      # code which writes to the DB

Requirements and design notes
=============================

We have multiple separate masters (not necessarily sharded). Let's call a
grouping of a master and its replicas a "DB set".

We would like to have read replicas of these masters, and we would like to read
from replicas as much as possible and we would like all writes to go to the
master of the set. But we would also like reads to be consistent to writers.

We would like this to be possible for web request cycles but also for units of
work like tasks or shell scripts. So we call this unit of work the "pinning
context".

Writes to a given master should continue to read from the master to avoid
inconsistency in the replication lag window, so there will be an API for
declaring that. Declaring (or otherwise preferring) that a set master is needed
is "pinning" and the group of pins for all DB sets is called the "pinned set".

Code which plans on writing (or needs the very lastest data) should be able to
declare that as early as possible to get a fully-consistent view from the
master(s).

It should be a clear error if we've made a mistake in pinning (that is, writing
after reading from a set). The issue here is that if we allow reads (not
knowing that a write is coming) that gives us an inconsistency window. For
example, a process reads from replica, gets a PK that has been deleted in
master, writes to master, fails. Or gets a PK that's been mutated in master so
that it shouldn't have been processed, etc.

Code which needs to write without pinning the whole container (e.g. a logging
table) should be able to side-step the pinning.

We should be able to manage the DB sets in settings with minimal repetition,
and it should compose well with multiple settings files.
       
Approach
--------

We use a threadlocal to hold the pinned set.

The database router will then respect pinned set.

The ``DATABASES`` dict in settings is "final" in the sense that it isn't
structured with any master/replica semantics. So we use an intermediate setting
for defining sets::

    MASTER_DATABASES = {
      'master-alias': { 'HOST':"a", ...normal settings },
       ...
    }
    
    DATABASE_SETS = { 
      'master-alias': [{'HOST':'someotherhost',...},], 
       # override some of the master settings
    }

And replica config can be finalized... ::

    DATABASES = DATABASES.update(populate_replicas(MASTER_DATABASES, DATABASE_SETS))

...resulting in something like... ::

    DATABASES = {
      'master-alias': { 'HOST':"a", ...normal settings },
      'master-alias-1': { 'HOST':"someotherhost", ...merged settings,
                          TEST_MIRROR='master-alias' },
      ...}

      
If no master is named "default", then the master of your first DB set will also
be aliased to "default". You should use
``django.utils.datastructures.SortedDict`` to make that stable.

If you have multiple database sets, you will also want to compose pinning with 
selection of the appropriate set.  For this, there is one additional setting: 
``DATABASE_ROUTER_DELEGATE``. It has the same interface as a normal 
``DATABASE_ROUTER``, but ``db_for_read`` and ``db_for_write`` must return only 
master aliases. Then an appropriate master or replica will be chosen for that DB 
set.

More concretely, suppose you have 2 different masters, and each of them has a read slave.  Your delegate router (as it existed before use of pindb) likely chooses which master based on app semantics.  Keep doing that.  Then pindb's router will select a read slave from the DB set whose master your existing (now delegate) router chose.

The strict router will throw an error if ``db_for_write`` is called without
declaring that it's OK. The correct approach is to pin the DB you intend to do
writes to *before you read* from a replica.

To explictly prefer a read replica despite pinning, use either... ::

    with pindb.unpinned_replica('master-alias'):
           ...

...or the ``.using`` method of a queryset.

If you would like to explicitly use a replica, ``pindb.get_replica()`` will
return a replica alias.

Pinning a set lasts the duration of a pinning context: once pinned, you should not
unpin a DB. If you want to write to a DB without pinning the container, you can
use queryset's ``.using`` method, which bypasses ``db_for_write``. Careful with
this axe.

To declare a pin... ::

    pindb.pin('master-alias')

TODO: Use signed cookies if available (dj 1.4+) for web pinning context.

Coverage
========

To see coverage of ``pindb``:

    $ PYTHONPATH=.:$PYTHONPATH coverage run setup.py test
    $ coverage html

Example configuration
=====================

::

    MASTER_DATABASES = {
        'default': {
            'NAME': 'db1',
            'ENGINE': DB_ENGINE,
            'USER': '...',
            'PASSWORD': '...',
            'HOST': '10.0.1.0',
            'PORT': 3306,
            'OPTIONS': DB_OPTIONS
        },
        'api': {
            'NAME': 'db2',
            'ENGINE': DB_ENGINE,
            'USER': '...',
            'PASSWORD': '...',
            'HOST': '10.0.2.0',
            'PORT': 3306,
            'OPTIONS': DB_OPTIONS
        },
    }
    
    DATABASE_SETS = {
        "default": [{'HOST': '10.0.1.1'},{'HOST': '10.0.1.2'}],
        "api": [{'HOST': '10.0.2.1'}]
    }
    
    DATABASES = {...}
    
    DATABASES.update(pindb.populate_replicas(MASTER_DATABASES, DATABASE_SETS))
    

    PINDB_DELEGATE_ROUTERS = ["myapp.router.Router"]
    DATABASE_ROUTERS = ['pindb.GreedyPinDbRouter']

    # default values which you can override:
    PINDB_ENABLED = True
    PINDB_PINNING_COOKIE = 'pindb_pinned_set'
    PINDB_PINNING_SECONDS = 15
