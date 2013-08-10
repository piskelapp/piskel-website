import sys
import os

DIR_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

EXTRA_PATHS = [
    DIR_PATH,
    os.path.join(DIR_PATH, 'lib', 'httplib2'),
    os.path.join(DIR_PATH, 'lib', 'oauth2'),
    os.path.join(DIR_PATH, 'lib', 'simpleauth')
]


def fix_sys_path(extra_extra_paths=()):
    """Fix the sys.path to include our extra paths."""
    extra_paths = EXTRA_PATHS[:]
    extra_paths.extend(extra_extra_paths)
    sys.path = extra_paths + sys.path
