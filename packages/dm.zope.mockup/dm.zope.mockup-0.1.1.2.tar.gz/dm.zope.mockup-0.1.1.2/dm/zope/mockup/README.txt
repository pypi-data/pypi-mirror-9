This is a (still small) repository with mockup objects to be used
in testsuites for Zope 2 applications and application components.

zodb
====

Usually, the ZODB (Zope Object Database) handles persistency transparently.
However, there are important exceptions: when a mutable attribute
of a persistent object is modified via its methods, the ZODB does not
know about these modifications. Without special measures, such
modifications are not persisted or persisted non-deterministically.
Such persistency bugs are difficult to detect and, therefore, should
be explicitely tested against. This module defines a ZODB mockup
connection which facilitates such tests.

The mockup connection has the following special methods:

``get_state`` (*obj*)
  return the current state of *obj* to be used later in ``verify_state``.

  As side effect, *obj* is registered with (added to) the connection
  (if necessary).

``verify_state`` (*state*)
  *state* must have been obtained by a previous call to ``get_state``.
  The call verifies that all modifications to the respective *obj* or
  its subcomponents are correctly registered with the ZODB.
  It raises an ``AssertionError`` with relevant information about the
  failing persistent subobjects.

  As side effect, new persistent subobjects encountered during the
  verification are registered with (added to) the connection.

  Due to http://bugs.python.org/issue12596, this
  currently works unreliably: Python 2.7 has introduced a (minor)
  optimization which suppresses ``BINPUT`` pickle instructions
  in some (rare) cases. As ``verify_state`` compares the historical
  pickle and the current one in order to detect modifications, this
  bug lets see it changes where there are none. The current release
  tries to work around this problem by not comparing the pickles verbatim
  but checking for equivalence modulo ``*PUT`` operations. The
  implemented equivalence is not perfect (e.g. it does not
  recognize that ``dumps(("spam", "spam"), 2)`` and
  ``dumps(("spaml"[:-1], "spaml"[:-1]), 2)`` are equivalent) but
  it might be sufficient for practical use.

``emulate_commit`` ()
  performs a savepoint which has similar effects as commit but
  will be undone by the next transaction abort.

The module's ``get_mockup_connection``() returns a mockup connection.
Behind this is a ``DemoStorage`` (i.e. a storage storing its state in memory).
In fact, ``get_mockup_connection`` returns a singleton connection, [re]opened,
associated with its own ``TransactionManager`` in an aborted transaction.

Following is typical test example:

>>> # elementary setup
... from persistent import Persistent
>>> from dm.zope.mockup.zodb import get_mockup_connection
>>> 
>>> class P(Persistent):
...   def __init__(self, id): self.id = id
...   # to get predictable output
...   def __repr__(self): return self.id
... 
>>> # work around for "python setup.py test" peculiarity
... import __builtin__; __builtin__.P = P
>>>
>>> c = get_mockup_connection()
>>> obj = P('obj')

>>> # normal attribute assignment
... state = c.get_state(obj)
>>> obj.l = []
>>> c.verify_state(state)

>>> # get_mockup_connection aborts the transaction
... #  in our case, it does not change the state of "obj" as
... #  this was newly created
... obj._p_changed
True
>>> c = get_mockup_connection()
>>> obj._p_changed
False

>>> # unregistered modification of mutable attribute
... state = c.get_state(obj)
>>> obj.l.append(1)
>>> c.verify_state(state)
Traceback (most recent call last):
  ...
AssertionError: ('unregistered modifications', [obj])

>>> # registered modification of mutable attribute
... state = c.get_state(obj)
>>> obj._p_changed = True
>>> obj.l.append(1)
>>> c.verify_state(state)

>>> # the same works for persistent subobjects as well
... c = get_mockup_connection()
>>> 
>>> obj0 = P('obj0')
>>> obj = obj0.obj = P('obj')
>>> 
>>> state = c.get_state(obj0)
>>> obj.l = []
>>> c.verify_state(state)
>>> c.emulate_commit()
>>> 
>>> state = c.get_state(obj0)
>>> obj.l.append(1)
>>> c.verify_state(state)
Traceback (most recent call last):
  ...
AssertionError: ('unregistered modifications', [obj])
>>>
>>> state = c.get_state(obj0)
>>> obj._p_changed = True
>>> obj.l.append(1)
>>> c.verify_state(state)
