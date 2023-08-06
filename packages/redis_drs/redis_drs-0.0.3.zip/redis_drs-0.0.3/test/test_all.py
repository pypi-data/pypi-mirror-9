# -*- coding: utf-8 -*-

import redis_drs
import time

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class TestAll(unittest.TestCase):

    def setUp(self):
        self.locker = redis_drs.Locker(resource_signature='myresourcesig')
        self.deleted_keys_store = '__deleted_keys__'

    def test_locking(self):

        # test re-unlock
        self.locker.lock()
        self.locker.unlock()
        self.assertRaises(redis_drs.LockMissing, self.locker.get)

        # test re-lock
        self.locker.lock()
        self.assertRaises(redis_drs.LockPresent, self.locker.lock)
        self.locker.unlock()

    def test_signature_immutability(self):
        def modify_sig():
            self.locker.resource_signature = 'I changed my mind'
        # resource_signature attribute should be "read-only"
        self.assertRaises(redis_drs.ConsistencyError, modify_sig)

    def test_monitor(self):
        def handle_deleted_keys(key):
            self.locker.server.rpush(self.deleted_keys_store, key)
        w = redis_drs.KeyRemovalWatcher(self.locker.server, handle_deleted_keys)
        self.locker.server.delete(self.deleted_keys_store)
        w.start_watch()
        self.locker.server.set('manual_delete', 'foo')
        self.locker.server.delete('manual_delete')
        self.locker.server.set('expired_key', 'foo', px=1)
        time.sleep(0.5)
        w.stop_watch()
        deleted_keys = self.locker.server.lrange(self.deleted_keys_store, 0, -1)
        self.assertEqual(deleted_keys, ['manual_delete', 'expired_key'])

if __name__ == '__main__':
   unittest.main()
