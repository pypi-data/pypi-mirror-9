# -*- coding: utf-8 -*-
"""
A Distributed Resource Scheduling system that uses Redis (and the python Redis library).

The presence of a key that contains a "resource_signature" indicates a lock. For conveniences' sake arbitrary data may
be associated with the resource_signature.

This package is heavily based upon the "redlock-py" package: https://github.com/SPSCommerce/redlock-py
"""

try:
    from .main import *
    from .monitor import *
except ImportError:
    import os
    if os.environ.get('I_AM_SETUP_SENTINEL') is None:
        raise
