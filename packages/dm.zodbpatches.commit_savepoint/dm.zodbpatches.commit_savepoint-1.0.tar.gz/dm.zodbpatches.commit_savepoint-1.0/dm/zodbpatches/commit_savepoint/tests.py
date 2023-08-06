import doctest
import unittest

# some doctest preliminaries
from persistent import Persistent
class P(Persistent): pass


class TestIssue2(unittest.TestCase):
  """Verify that https://github.com/zopefoundation/ZODB3/issues/2 is fixed."""
  def test_issue_fixed(self):
    '''Doctest from ticket.
>>> # preliminaries
>>> from ZODB.DB import DB
>>> import transaction
>>> def access(o):
...   """emulate access to *o*."""
...   o._p_deactivate() # simulate cache eviction
...   o._p_activate() # simulate access
... 
>>> # test `MappingStorage`
>>> from ZODB.MappingStorage import MappingStorage
>>> 
>>> db = DB(MappingStorage())
>>> T = transaction.get()
>>> c = db.open()
>>> o = P()
>>> c.add(o)
>>> sp = T.savepoint()
>>> # access still works
>>> access(o)
>>> c.tpc_begin(T)
>>> # access still works
>>> access(o)
>>> c.commit(T)
>>> # access must not fail
>>> access(o)
>>> c.tpc_vote(T)
>>> c.tpc_finish(T)
>>> # access works again
>>> access(o)
>>> T.abort()
'''

def test_suite():
    s = unittest.TestSuite((doctest.DocTestSuite(),))
    # verify the `testConnection` tests still succeed
    from ZODB.tests import testConnection
    s.addTest(testConnection.test_suite())
    # verify the `testConnectionSavepoint` tests still succeed
    from ZODB.tests import testConnectionSavepoint
    s.addTest(testConnectionSavepoint.test_suite())
    return s
  
    
