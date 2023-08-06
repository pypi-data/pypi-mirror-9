# Copyright (C) 2015 by Dr. Dieter Maurer <dieter@handshake.de>
"""(Monkey) patches working around https://github.com/zopefoundation/ZODB3/issues/2."""
from logging import getLogger

from ZODB.Connection import Connection

logger = getLogger(__name__)


ori_commit = Connection.commit.im_func
ori_tpc_vote = Connection.tpc_vote.im_func
ori_tpc_finish = Connection.tpc_finish.im_func

def commit(self, transaction):
  ori_close = None
  savepoint_storage = self._savepoint_storage
  if savepoint_storage is not None:
    # prevent storage closing
    ori_close = savepoint_storage.close
    savepoint_storage.close = lambda:None
  try:
    ori_commit(self, transaction)
    # undo the storage switch done by `_commit_savepoint`
    if savepoint_storage is not None and self._savepoint_storage is None:
      self._storage = self._savepoint_storage = savepoint_storage
  finally:
    if ori_close is not None:
      # allow storage closing again
      #  avoid an unnecessary cycle
      #savepoint_storage.close = ori_close
      del savepoint_storage.close


def tpc_vote(self, transaction):
  savepoint_storage = self._savepoint_storage
  if savepoint_storage is not None:
    # redo the storage switch undone by `commit`
    self._storage = self._normal_storage
    self.savepoint_storage = None
  ori_tpc_vote(self, transaction)
  if savepoint_storage is not None:
    # reundo the storage switch
    self._storage = self._savepoint_storage = savepoint_storage

def tpc_finish(self, transaction):
  savepoint_storage = self._savepoint_storage
  if savepoint_storage is not None:
    # redo the storage switch undone by `commit`
    self._storage = self._normal_storage
    self._savepoint_storage = None
  ori_tpc_finish(self, transaction)  

Connection.commit = commit
Connection.tpc_vote = tpc_vote
Connection.tpc_finish = tpc_finish

logger.info("Patched `ZODB.Connection.Connection` to work around https://github.com/zopefoundation/ZODB3/issues/2")
