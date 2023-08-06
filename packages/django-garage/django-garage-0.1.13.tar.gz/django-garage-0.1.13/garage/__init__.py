# -*- coding: utf-8 -*-
"""
garage

Utilities and helpers functions.

* created: 2011-02-15 Kevin Chan <kefin@makedostudio.com>
* updated: 2015-03-02 kchan
"""

from __future__ import (absolute_import, unicode_literals)

import warnings

try:
    from django.core.exceptions import ImproperlyConfigured
    from django.conf import settings as _django_settings
except (ImportError, ImproperlyConfigured):
    from garage.utils import DataObject
    _django_settings = DataObject()
    warnings.warn('Unable to import Django settings! Please check your setup '
                  'and make sure Django is installed and your project settings '
                  'are loaded correctly.', RuntimeWarning)



# package version
__author__ = 'Kevin Chan'
__version_info__ = (0, 1, 13)
__version__ = '.'.join(map(str, __version_info__))

VERSION = __version_info__

def get_version(version=None):
    """
    Returns a PEP 440 version string (in the form of major.minor.micro).
    Http://legacy.python.org/dev/peps/pep-0440/
    """
    if version is None:
        version = __version_info__
    if isinstance(version, (list, tuple)):
        version = '.'.join(map(str, version))
    return version


# helper functions and shortcuts

# get setting

def get_setting(name, default=None):
    """Retrieve attribute from settings."""
    return getattr(_django_settings, name, default)


# legacy functions for compatibility with old code using this package

def resp(request, template, context):
    """Shortcut for render_to_response()."""
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    return render_to_response(template, context,
                              context_instance=RequestContext(request))


# for compatibility with old code that imports the following from here
from garage.session import set_session_var, get_session_var
