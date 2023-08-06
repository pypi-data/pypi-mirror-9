from __future__ import unicode_literals
from __future__ import print_function

import os
import os.path


def find_conf():
    """Finds a dataplicity.conf file in the current working directory, or ancestors"""
    path = os.path.abspath(os.path.expanduser(os.getcwd()))
    while path not in ('', '/'):
        conf_path = os.path.join(path, 'dataplicity.conf')
        if os.path.exists(conf_path):
            return conf_path
        path = os.path.dirname(path)
    return None


def parse_lines(s):
    """Split a setting in to a list"""
    return [l.strip() for l in s.splitlines() if l.strip()]
