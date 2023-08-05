import logging
import os

GITHUB_SSH_CONFIG = '''
# devassistant config for user {login}
Host github.com-{login}
    HostName github.com
    User git
    IdentityFile ~/.ssh/{keyname}'''
GITHUB_SSH_KEYNAME = 'id_rsa_devassistant_{login}'

LOG_FORMATS_MAP = {'log_cmd': u'{levelname}: {msg}',
                   'cmd_call': u'[devassistant]$ {msg}',
                   'cmd_out': u'{msg}',
                   'cmd_retcode': u'> retcode: {msg}',
                   'sub_da': u'{msg}'}
LOG_LEVELS_MAP = {'d': 'DEBUG', 'i': 'INFO', 'w': 'WARNING', 'e': 'ERROR', 'c': 'CRITICAL'}
LOG_SHORT_TO_NUM_LEVEL = {}
for level_short, level_name in LOG_LEVELS_MAP.items():
    LOG_SHORT_TO_NUM_LEVEL[level_short] = getattr(logging, level_name)

LAST_LR_VAR = 'LAST_LRES'
LAST_R_VAR = 'LAST_RES'

ROOT_EXECUTABLE = '/usr/libexec/da_auth'

SUBASSISTANT_PREFIX = 'subassistant'
SUBASSISTANT_N_STRING = 'subassistant_{0}'

DEPS_ONLY_FLAG = '--deps-only'

# NOTE: data directories should always be absolute paths, since
# - theoretically, if DevAssistant would change working directory and *then* try to
#   load assistants, the relative path would point in an unwanted location
# - command runners should be allowed to rely on this (e.g. if we pass a file from files
#   section to Jinja2Runner, we need to make sure it's fullpath)
DATA_DIRECTORIES = [os.path.expanduser('~/.devassistant'),
                    '/usr/local/share/devassistant',
                    '/usr/share/devassistant/']
DEVASSISTANT_HOME = DATA_DIRECTORIES[0]
if 'DEVASSISTANT_PATH' in os.environ:
    DATA_DIRECTORIES = [os.path.abspath(os.path.expanduser(p))
        for p in os.environ['DEVASSISTANT_PATH'].split(':')] + DATA_DIRECTORIES
if 'DEVASSISTANT_HOME' in os.environ:
    DEVASSISTANT_HOME = os.path.abspath(os.path.expanduser(os.environ['DEVASSISTANT_HOME']))

USE_CACHE = True
CACHE_FILE = os.path.join(DEVASSISTANT_HOME, '.cache.yaml')
CONFIG_FILE = os.path.join(DEVASSISTANT_HOME, '.config')
LOG_FILE = os.path.join(DEVASSISTANT_HOME, 'lastrun.log')

ASSISTANT_ROLES = ['crt', 'twk', 'prep', 'extra']
DEFAULT_ASSISTANT_ROLE = 'crt'

# system dependency types and package managers for various distros
# more distros can have the same system deptype, but different manager
SYSTEM_DEPTYPES_SHORTCUTS = {'rpm': ['fedora', 'red hat enterprise linux', 'redhat', 'rhel',
                                     'centos', 'suse'],
                             'pacman': ['arch'],
                             # NOTE /etc/os-release has ID=gentoo,
                             # but platform.distribution reports "Gentoo Base System" string
                             'ebuild': ['gentoo', 'gentoo base system'],
                             'homebrew': ['darwin', 'OS X']}

DAPI_DEFAULT_API_URL = 'https://dapi.devassistant.org/api/'
DAPI_DEFAULT_USER_INSTALL = '~/.devassistant'
DAPI_DEFAULT_ROOT_INSTALL = '/usr/local/share/devassistant'
