# -*- coding: utf-8 -*-

import redis_drs

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class TestAll(unittest.TestCase):

    def setUp(self):
        self.locker = redis_drs.Locker(resource_signature='myresourcesig')

    def test_all(self):

        self.locker.lock(resource_info={'bob', 'mary'})
        self.locker.get()
        self.locker.update({'7':99})
        self.locker.get()
        self.locker.unlock()

        # should be unlocked
        self.assertRaises(redis_drs.LockMissing, self.locker.get)

        self.locker.lock()
        # should be locked
        self.assertRaises(redis_drs.LockPresent, self.locker.lock)

        def modify_sig():
            self.locker.resource_signature = 'I changed my mind'
        # resource_signature attribute should be "read-only"
        self.assertRaises(redis_drs.ConsistencyError, modify_sig)

if __name__ == '__main__':
   unittest.main()
