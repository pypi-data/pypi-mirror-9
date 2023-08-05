# -*- coding: utf-8 -*-
"""Config file for isbntools."""

# Special files
CACHE_FILE = '.metacache'


# Paths
CONF_PATH = None


def setconfpath(path):
    """Set the directory of the conf file."""
    global CONF_PATH
    CONF_PATH = path


# Timeouts
SOCKETS_TIMEOUT = 12    # seconds
THREADS_TIMEOUT = 11    # seconds


def setthreadstimeout(seconds):
    """Set the value of THREADS_TIMEOUT (in seconds)."""
    global THREADS_TIMEOUT
    THREADS_TIMEOUT = seconds


# API keys
apikeys = {}


def add_apikey(service, apikey):  # pragma: no cover
    """Add API keys.

    add_apikey('isbndb', 'JuHytr6') [is fake!]
    """
    apikeys[service] = apikey


# Generic Options
options = {}


def set_option(option, value):    # pragma: no cover
    """Set the value for option."""
    options[option] = value
