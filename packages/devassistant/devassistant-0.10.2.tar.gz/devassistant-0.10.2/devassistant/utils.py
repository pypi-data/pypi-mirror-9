from __future__ import print_function

import os
import platform
import sys

import six
import yaml
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

try:  # ugly hack for using imp instead of importlib on Python <= 2.6
    import importlib
    import importlib.machinery
except ImportError:
    import imp as importlib
    importlib.machinery = None

    def import_module(name):
        fp, pathname, description = importlib.find_module(name.replace('.', '/'))
        return importlib.load_module(name, fp, pathname, description)
    importlib.import_module = import_module
    del import_module

from devassistant import settings


def import_module(module):
    return importlib.import_module(module)


def import_by_path(modname, path):
    if importlib.machinery:  # Python >= 3.3
        loader = importlib.machinery.SourceFileLoader(modname, path)
        return loader.load_module()
    else:  # Python 2.6, 2.7
        return importlib.load_source(modname, path)


def get_system_name():
    return platform.system().lower()


def get_system_version():
    return platform.release().lower()


def get_distro_name():
    system = get_system_name()
    if system == 'linux':
        return platform.linux_distribution(full_distribution_name=False)[0].lower() \
            or _get_os_release_content('ID')
    elif system == 'darwin':
        return 'darwin'
    else:
        return ''


def get_distro_version():
    return platform.linux_distribution()[1].lower() or _get_os_release_content('VERSION_ID')


def _get_os_release_content(line_start):
    os_release = '/etc/os-release'
    if not os.path.exists(os_release):
        return ''

    with open(os_release) as osrel:
        for l in osrel.readlines():
            if l.startswith(line_start):
                found = l.split('=')[-1].strip()
    return found.lower()


def get_cwd_or_homedir():
    try:
        return os.getcwd()
    except:
        return os.path.expanduser('~')


def cl_string_for_da_eval(section, context=None):
    if context is None:
        context = {}
    # filter variables that we don't want to pass from context
    unwanted = ['__assistant__', '__section__']
    ctxt_to_dump = dict(filter(lambda i: i[0] not in unwanted, context.items()))

    dumped = yaml.dump({'ctxt': ctxt_to_dump, 'run': section}, stream=None, Dumper=Dumper)
    dumped_in_heredoc = '\n'.join(['\VERY_LONG_RANDOM_EOF', dumped, 'VERY_LONG_RANDOM_EOF'])

    cl_string = ' '.join([sys.executable,
                          '-m devassistant.cli.cli_runner',
                          'eval - <<',
                          dumped_in_heredoc])
    return cl_string


def find_file_in_load_dirs(relpath):
    """If given relative path exists in one of DevAssistant load paths,
    return its full path.

    Args:
        relpath: a relative path, e.g. "assitants/crt/test.yaml"

    Returns:
        absolute path of the file, e.g. "/home/x/.devassistant/assistanta/crt/test.yaml
        or None if file is not found
    """
    if relpath.startswith(os.path.sep):
        relpath = relpath.lstrip(os.path.sep)

    for ld in settings.DATA_DIRECTORIES:
        possible_path = os.path.join(ld, relpath)
        if os.path.exists(possible_path):
            return possible_path


def add_no_cache_argument(parser):
    # This really only stores the True/False value. We need to set
    # settings.USE_CACHE before we create the parser, but for creating
    # the parser, we need to load assistants. That means we set
    # settings.USE_CACHE in cli_runner and gui/__init__ according to sys.argv.
    parser.add_argument('--no-cache',
                        help='Don\'t use assistants cache (useful for debugging).',
                        action='store_true',
                        dest='da_no_cache',
                        default=False)


_exithandlers = []


def atexit(func, *targs, **kargs):
    _exithandlers.append((func, targs, kargs))
    return func


def run_exitfuncs():
    """Function that behaves exactly like Python's atexit, but runs atexit functions
    in the order in which they were registered, not reversed.
    """
    exc_info = None
    for func, targs, kargs in _exithandlers:
        try:
            func(*targs, **kargs)
        except SystemExit:
            exc_info = sys.exc_info()
        except:
            exc_info = sys.exc_info()

    if exc_info is not None:
        six.reraise(exc_info[0], exc_info[1], exc_info[2])
