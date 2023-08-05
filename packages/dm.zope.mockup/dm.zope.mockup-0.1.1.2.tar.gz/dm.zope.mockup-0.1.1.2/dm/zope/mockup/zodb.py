# Copyright (C) 2010-2015 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
"""ZODB related mockups

See ``README.txt`` for documentation.
"""
from persistent import Persistent
from transaction._manager import TransactionManager
from pickletools import genops
from cStringIO import StringIO

from ZODB.Connection import Connection, ObjectWriter
from ZODB.DemoStorage import DemoStorage
from ZODB.DB import DB


class MockupConnection(Connection):
  """mockup connection to facilitate tests checking proper modification registration."""

  def get_state(self, obj):
    assert isinstance(obj, Persistent)
    if obj._p_jar is None: self.add(obj)
    assert obj._p_jar is self
    writer = _MockupObjectWriter(obj)
    return [(sobj, writer.serialize(sobj)) for sobj in writer]

  def verify_state(self, state):
    errors = []
    # from dm import pdb; pdb.set_trace()
    for obj, old_state in state:
      writer = ObjectWriter(obj)
      if not (obj._p_changed or equivalent(old_state, writer.serialize(obj))):
        errors.append(obj)
      for new_obj in writer._stack[1:]:
        if new_obj._p_jar is None: self.add(new_obj)
    if errors:
      raise AssertionError('unregistered modifications', errors)

  def emulate_commit(self):
    """create a savepoint in order to emulate a commit."""
    self.transaction_manager.savepoint()

  # work around https://bugs.launchpad.net/zodb/+bug/615758
  def _abort(self):
    for obj in self._added.itervalues(): obj._p_changed = False
    super(MockupConnection, self)._abort()
  


_mockup_connection_singleton = None

def get_mockup_connection():
  global _mockup_connection_singleton
  c = _mockup_connection_singleton
  if c is not None:
    c.transaction_manager.get().abort()
    # ZODB 3.8 used '_opened'; ZODB 3.9 'opened'
    c.opened = c._opened = None # prevent returning to connection pool
    c.close()
  else:
    c = _mockup_connection_singleton = MockupConnection(DB(DemoStorage()))
  c.open(TransactionManager())
  return c


class _MockupObjectWriter(ObjectWriter):
  """``ObjectWriter`` registering any persistent subobject, not just new ones."""
  _seen = None

  def persistent_id(self, obj):
    r = ObjectWriter.persistent_id(self, obj)
    if r is not None and obj not in self._stack:
      seen = self._get_seen()
      if obj._p_oid not in seen:
        self._stack.append(obj)
        seen.add(obj._p_oid)
    return r

  def _get_seen(self):
    seen = self._seen
    if seen is None: seen = self._seen = set()
    return seen


def equivalent(o1, o2):
  """True, if object states *o1* and *o2* are equivalent."""
  p1 = StringIO(o1); p2 = StringIO(o2)
  # object states consist of 2 consective pickles -- class and (proper) state
  return _equivalent(p1, p2) and _equivalent(p1, p2)

def _equivalent(p1, p2):
  """True, if pickles *p1* and *p2* are equivalent."""
  # this does not work due to http://bugs.python.org/issue12596
  #return p1 == p2
  # Try to work around by considering equivalence up to "PUT"s.
  #  This is not complete, as it does not recognize the equivalence
  #  of `dumps(("spam", "spam"), 2)` and
  #  `dumps(("spaml"[:-1], "spaml"[:-1]), 2)` but
  #  it might be enough for practical cases
  mm = {}
  g1 = genops(p1); g2 = genops(p2)
  x1 = g1.next(); x2 = g2.next()
  while True:
    if x1[:2] == x2[:2]:
      if x1[0].code == ".": return True
      x1 = g1.next(); x2 = g2.next()
      continue
    op1 = x1[0]; op2 = x2[0]
    if op1 != op2:
      # we have differing opcodes - we allow this only,
      #  if one of them is a (redundant) put
      #  We ignore the put; should it not have been redundant, we
      #  will learn this later
      if "PUT" in op1.name: x1 = g1.next(); continue # assume redundant put
      if "PUT" in op2.name: x2 = g2.next(); continue # assume redundant put
      return False
    # opcodes are identical -- i.e. the args differ
    a1 = x1[1]; a2 = x2[1]
    if "PUT" in op1.name: mm[a1] = a2
    elif "GET" in op1.name and mm[a1] != a2: return False
    x1 = g1.next(); x2 = g2.next()
    

