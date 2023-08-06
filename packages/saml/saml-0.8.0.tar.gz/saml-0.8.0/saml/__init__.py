# -*- coding: utf-8 -*-
"""
A python interface to produce and consume Security Assertion Markup
Language (SAML) v2.0 messages.

See: https://www.oasis-open.org/standards#samlv2.0
"""
# Version of the library.
from ._version import __version__, __version_info__  # noqa

# Version of the SAML standard supported.
from .schema import VERSION as SAML_VERSION

from .signature import sign, verify
from . import client

VERSION = __version__

__all__ = [
    'VERSION',
    'SAML_VERSION',
    'sign',
    'verify',
    'client'
]
