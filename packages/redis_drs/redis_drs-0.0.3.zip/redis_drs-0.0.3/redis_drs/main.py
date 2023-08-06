# -*- coding: utf-8 -*-
"""
Started life as:
    https://github.com/SPSCommerce/redlock-py
    by: webapps@spscommerce.com
"""

import redis
import time
import pickle

class RedisDRSError(Exception):
    ""

class LockPresent(RedisDRSError):
    ""

class LockMissing(RedisDRSError):
    ""

class ConsistencyError(RedisDRSError):
    ""

class LockAquisitionFailed(RedisDRSError):
    ""

class ValueModificationFailed(RedisDRSError):
    ""

class Locker(object):

    clock_drift_factor = 0.01
    _default_ttl = 2 * 24 * 60 * 60 * 1000  #  TWO DAYS
    _resource_signature = None

    def __init__(self, resource_signature, *args, **kwargs):

        attrs = ['default_ttl',]
        for attr in attrs:
            setattr(self, attr, kwargs.pop(attr, None))
        self._resource_signature = resource_signature
        if self.default_ttl is None:
            self.default_ttl = self._default_ttl
        self.server = redis.StrictRedis(*args, **kwargs)

    def normalize_resource_signature(self, resource_signature):
        return resource_signature

    @property
    def resource_signature(self):
        return self.normalize_resource_signature(self._resource_signature)

    def serialize(self, obj):
        return obj

    def unserialize(self, string):
        return string

    @resource_signature.setter
    def resource_signature(self, value):
        raise ConsistencyError('An attempt to reset resource_signature was made.')

    def update(self, resource_info):
        if self.resource_signature not in self.server:
            raise LockMissing('Expected server {0} to be locked for resource signature {1}'.format(self.server, self.resource_signature))
        else:
            resource_info = self.serialize(resource_info)
            result = self.server.set(self.resource_signature, resource_info, nx=False, xx=True)
            if not result:
                raise ValueModificationFailed('Could not get lock for resource signature {0}'.format(self.resource_signature))

    def get(self):
        if self.resource_signature not in self.server:
            raise LockMissing('Expected server {0} to be locked for resource signature {1}'.format(self.server, self.resource_signature))
        else:
            resource_info = self.server.get(self.resource_signature)
            if resource_info is None:
                raise ConsistencyError('Value for resource signature {0} was None, yet the key was present.'.format(self.resource_signature))
            return self.unserialize(resource_info)

    def lock(self, resource_info='', ttl=None):

        if ttl is None:
            ttl = self.default_ttl

        drift = int(ttl * self.clock_drift_factor) + 2

        start_time = int(time.time() * 1000)
        if self.resource_signature in self.server:
            raise LockPresent('server {0} already has a lock for resource signature {1}'.format(self.server, self.resource_signature))
        else:
            resource_info = self.serialize(resource_info)
            result = self.server.set(self.resource_signature, resource_info, nx=True, px=ttl)  # nx=True required!
            if not result:
                raise LockAquisitionFailed('Could not get lock for resource signature {0}'.format(self.resource_signature))
        elapsed_time = int(time.time() * 1000) - start_time
        validity = int(ttl - elapsed_time - drift)
        if validity <= 0:
            if self.resource_signature in self.server:
                raise ConsistencyError('resource_signature {0} for server {1} '
                                       'should have expired, but the lock is still there.'.format(self.resource_signature, self.server))
            else:
                raise LockAquisitionFailed('It seem that the lock for resource_signature {0} on {1} '
                                           'has already expired. (ttl too small?)'.format(self.resource_signature, self.server))

        return result

    def unlock(self):  # FIXME: non-atomic
        if self.resource_signature not in self.server:
            raise LockMissing('Expected server {0} to be locked for resource signature {1}'.format(self.server, self.resource_signature))
        retval = self.get()
        self.server.delete(self.resource_signature)
        return retval
