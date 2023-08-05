import os
import json
import collections
import leveldb
import logging
from cached_property import cached_property

from .utils import memoized
from .offset import OffsetTracker

logger = logging.getLogger('pymza.state')


class StateManager(object):
    def __init__(self, state_dir):
        self.state_dir = state_dir
        # self.task_states = {}
        # self.task_offsets = {}

    def get_task_state_manager(self, task, partition_id):
        if isinstance(task, basestring):
            task_name = task
        else:
            task_name = task.name

        return self._do_get_task_state_manager((task_name, partition_id))

    @memoized
    def _do_get_task_state_manager(self, key):
        task_name, partition_id = key
        task_state_path = os.path.join(self.state_dir, task_name, str(partition_id))
        return TaskStateManager(task_name, partition_id, task_state_path)

OFFSET_PREFIX = '__offsets_'

def encode_key(key):
    if isinstance(key, unicode):
        key = key.encode('utf-8')
    return key


class TaskStateManager(object):
    def __init__(self, task_name, partition_id, state_dir):
        self.task_name = task_name
        self.partition_id = partition_id

        if not os.path.exists(state_dir):
            os.makedirs(state_dir)

        try:
            self.db = leveldb.LevelDB(state_dir)
        except leveldb.LevelDBError:
            logger.error('Failed to open LevelDB for task %s:%s at path %s',
                         task_name, partition_id, state_dir)
            raise

    def get_key(self, key):
        return json.loads(self.db.Get(encode_key(key)))

    def iterate_keys(self, key_from=None, key_to=None, reverse=False):
        # hack to ensure that range returns all keys
        if self.state.is_modified:
            self.commit_state()
        for key in self.db.RangeIter(include_value=False, key_from=key_from, key_to=key_to, reverse=reverse):
            if not key.startswith('__'):
                yield key

    def iterate_key_values(self, key_from=None, key_to=None, reverse=False):
        # hack to ensure that range returns all keys
        if self.state.is_modified:
            self.commit_state()
        return ((k, json.loads(v)) for k, v in self.db.RangeIter(include_value=True, key_from=key_from, key_to=key_to, reverse=reverse) if not k.startswith('__'))

    def commit_state(self):
        state = self.state
        batch = leveldb.WriteBatch()
        for key in state._changes:
            batch.Put(encode_key(key), json.dumps(state._cache[key]))
        for key in state._deletes:
            batch.Delete(encode_key(key))
        self.db.Write(batch)

    @cached_property
    def state(self):
        return TaskState(self)

    @cached_property
    def offsets(self):
        offsets = {}
        prefix_len = len(OFFSET_PREFIX)

        for key, val in self.db.RangeIter(key_from=OFFSET_PREFIX):
            if not key.startswith(OFFSET_PREFIX):
                break
            topic, partition = key[prefix_len:].split(':', 1)
            partition = int(partition)
            offset = int(val)
            offsets[topic] = offset
        return OffsetTracker(offsets)

    def commit_offsets(self):
        batch = leveldb.WriteBatch()
        for topic, offset in self.offsets:
            batch.Put('{0}{1}:{2}'.format(OFFSET_PREFIX, topic, self.partition_id), str(offset))
        self.db.Write(batch)
        self.offsets.reset_is_modified()


class TaskState(collections.MutableMapping):
    def __init__(self, state_manager):
        self._mgr = state_manager
        self._cache = {}
        self._deletes = set()
        self._changes = set()

    def __getitem__(self, key):
        if key in self._deletes:
            raise KeyError(key)

        if key in self._cache:
            return self._cache[key]
        else:
            value = self._mgr.get_key(key)
            self._cache[key] = value
            return value

    def __setitem__(self, key, value):
        self._deletes.discard(key)
        self._cache[key] = value
        self._changes.add(key)

    def __delitem__(self, key):
        if key in self._cache:
            del self._cache[key]
        self._deletes.add(key)
        self._changes.discard(key)

    def __iter__(self):
        return self.iterkeys()

    def __len__(self):
        raise RuntimeError('Calculating length of state is not supported')

    # expose RangeIter api
    def range(self, key_from=None, key_to=None, include_value=True, reverse=False):
        if include_value:
            return self._mgr.iterate_key_values(key_from=key_from, key_to=key_to, reverse=reverse)
        else:
            return self._mgr.iterate_keys(key_from=key_from, key_to=key_to, reverse=reverse)

    # improved methods
    def iteritems(self):
        return self.range()

    def iterkeys(self):
        return self._mgr.iterate_keys()

    def itervalues(self):
        for (k, v) in self.iteritems():
            yield v

    def keys(self):
        # fixes default method which calls __len__
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def has_key(self, key):
        return key in self

    @property
    def is_modified(self):
        return self._changes or self._deletes

    def commit(self):
        self._mgr.commit_state()
        self._changes = set()
        self._deletes = set()
        self._cache = {}

    def clear(self):
        for key in self.iterkeys():
            del self[key]
