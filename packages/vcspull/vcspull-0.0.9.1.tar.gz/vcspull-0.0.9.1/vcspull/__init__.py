#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manage multiple git, mercurial, svn repositories from a YAML / JSON file.

vcspull
~~~~~~~

:copyright: Copyright 2013-2015 Tony Narlock.
:license: BSD, see LICENSE for details

"""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

from .util import (
    expand_config, get_repos, mkdir_p, run, scan, which, update_dict
)
from .log import (
    LogFormatter, DebugLogFormatter, RepoLogFormatter, RepoFilter
)
from .cli import (
    ConfigFileCompleter, command_load, find_configs, get_parser,
    get_repos_new, in_dir, is_config_file, load_configs, main, scan_repos,
    setup_logger, validate_schema
)

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
