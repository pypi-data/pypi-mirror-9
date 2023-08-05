"""Cubicweb intregration with `transaction`

Based on zope.sqlalchemy one phase SessionDataManager"""

from __future__ import absolute_import

from zope.interface import implementer
from transaction.interfaces import ISavepointDataManager


@implementer(ISavepointDataManager)
class CWDataManager(object):
    """Integrate a CubicWeb cnx into a zope transaction

    One phase only (two-phase is not yet supported by cubicweb)

    Doesn't define 'savepoint' as cw cnx does not support subtransactions
    """

    def __init__(self, cnx, transaction_manager):
        self.transaction_manager = transaction_manager
        self.cnx = cnx
        transaction_manager.get().join(self)
        self.state = 'init'
        print "JOINED"

    def _finish(self, final_state):
        print "FINISHING", final_state
        self.state = final_state

    def abort(self, transaction):
        self.cnx.rollback()
        self._finish('aborted')

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        pass

    def tpc_vote(self, transaction):
        self.cnx.commit()
        self._finish('commited')

    def tpc_finish(self, transaction):
        self.cnx.__exit__()

    def tpc_abort(self, transaction):
        assert self.state is not 'commited'
        self.cnx.rollback()
        self._finish('aborted')

    def sortKey(self):
        # Try to sort last, so that we vote last - we may commit in tpc_vote(),
        # which allows Zope to roll back its transaction if the RDBMS
        # threw a conflict error.
        return "~cw:%d" % id(self.cnx)
