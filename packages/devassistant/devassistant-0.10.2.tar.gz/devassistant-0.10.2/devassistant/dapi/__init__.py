import os
import tarfile
import yaml
import re
import logging
import hashlib
try:
    from yaml import CLoader as Loader
except:
    from yaml import Loader
from . import licenses, platforms
from devassistant.exceptions import DapFileError, DapMetaError, DapInvalid
from devassistant.logger import logger


class Dap(object):
    '''Class representing a dap

    Everything should be considered read-only. If not, things might blow up.'''

    _icons = 'svg|png'

    _required_meta = set('package_name version license authors summary'.split())
    _optional_meta = set('homepage bugreports description dependencies supported_platforms'.
        split())
    _array_meta = set('authors dependencies supported_platforms'.split())

    _url_pattern = r'(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&%\$\-]+)*@)*' \
                   r'(([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(museum|[a-z]{2,4}))' \
                   r'(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\?\'\\\+&%\$#\=~_\-]+))*'
    _email_pattern = r'[^@]+(@|_at_)([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(museum|[a-z]{2,4})'
    _name_pattern = r'([a-z][a-z0-9\-_]*[a-z0-9]|[a-z])'
    _version_pattern = r'([0-9]|[1-9][0-9]*)(\.([0-9]|[1-9][0-9]*))*(dev|a|b)?'

    _meta_valid = {'package_name': re.compile(r'^' + _name_pattern + r'$'),
                   'version': re.compile(r'^' + _version_pattern + r'$'),
                   'license': licenses,
                   'summary': re.compile(r'^[^\n]+$'),
                   'homepage': re.compile(r'^' + _url_pattern + r'$'),
                   'bugreports': re.compile(r'^(' + _email_pattern + '|' + _url_pattern + ')$'),
                   'description': re.compile(r'.+'),
                   'authors': re.compile(r'^(\w+[\w \.]*[\w\.-]+|\w)( +<' + _email_pattern +
                       '>)?$', re.UNICODE),
                   'dependencies': re.compile(r'^' + _name_pattern + r'( *(<|>|<=|>=|==) *' +
                       _version_pattern + r')?$'),
                   'supported_platforms': platforms}

    _assistants = re.compile(r'(assistants|snippets)/.*\.yaml')

    def __init__(self, dapfile, fake=False, mimic_filename=None):
        '''Constructor, takes dap file location as argument.
        Loads the dap if at least somehow valid.
        If fake is True, it fill not open any files, but creates a fake dap'''
        self._badmeta = {}
        if fake:
            if mimic_filename:
                self.basename = mimic_filename
            else:
                self.basename = 'fake.dap'
            self.files = []
            self.meta = {}
            return

        if mimic_filename:
            self.basename = mimic_filename
        else:
            self.basename = os.path.basename(dapfile)

        try:
            self._tar = tarfile.open(dapfile, mode='r:gz')
        except tarfile.ReadError as e:
            raise DapFileError('%s is not a tar.gz archive' % self.basename)
        except IOError as e:
            raise DapFileError(e)
        metas = set()
        self.files = self._tar.getnames()
        for f in self.files:
            if os.path.basename(f) == 'meta.yaml' and os.path.dirname(f).count('/') == 0:
                metas.add(f)
        if not metas:
            raise DapMetaError('Could not find any meta.yaml in %s' % self.basename)
        if len(metas) > 1:
            raise DapMetaError('Multiple meta.yaml files found in %s (%s)' %
                (self.basename, ', '.join(metas)))
        self._meta_location = metas.pop()
        self._load_meta(self._get_file(self._meta_location))
        self.sha256sum = hashlib.sha256(open(dapfile, 'rb').read()).hexdigest()

    def _get_file(self, path):
        '''Extracts a file from dap to a file-like object'''
        extracted = self._tar.extractfile(path)
        if extracted:
            return extracted
        raise DapFileError(('Could not read %s from %s, maybe it\'s a directory,' +
            'bad link or the dap file is corrupted') % (path, self.basename))

    def _load_meta(self, meta):
        '''Load data from meta.yaml to a dictionary'''
        self.meta = yaml.load(meta.read(), Loader=Loader)

        # Versions are often specified in a format that is convertible to an
        # int or a float, so we want to make sure it is interpreted as a str.
        # Fix for the bug #300.
        try:
            self.meta['version'] = str(self.meta['version'])
        except KeyError:
            pass

    def _report_problem(self, problem, level=logging.ERROR):
        '''Report a given problem'''
        problem = self.basename + ': ' + problem
        if self._logger.isEnabledFor(level):
            self._problematic = True
        if self._check_raises:
            raise DapInvalid(problem)
        self._logger.log(level, problem)

    def _isvalid(self, datatype):
        '''Checks if the given datatype is valid in meta'''
        try:
            return bool(Dap._meta_valid[datatype].match(self.meta[datatype]))
        except KeyError:
            self.meta[datatype] = ''
            return datatype in Dap._optional_meta

    def _arevalid(self, datatype):
        '''Checks if the given datatype is valid in meta (for array-like types)'''
        try:
            if not isinstance(self.meta[datatype], list):
                return False, []
        except KeyError:
            self.meta[datatype] = []
            return datatype in Dap._optional_meta, []
        if not self.meta[datatype]:
            return datatype in Dap._optional_meta, []
        duplicates = set([x for x in self.meta[datatype] if self.meta[datatype].count(x) > 1])
        if duplicates:
            return False, list(duplicates)
        ret = []
        for item in self.meta[datatype]:
            if not Dap._meta_valid[datatype].match(item):
                ret.append(item)
        self._badmeta[datatype] = ret
        return not bool(ret), ret

    def _check_meta(self):
        '''Check the meta.yaml in the dap
        Only call this from check()'''
        # Check for non array-like metadata
        for datatype in (Dap._required_meta | Dap._optional_meta) - Dap._array_meta:
            if not self._isvalid(datatype):
                self._report_problem(datatype + ' is not valid (or required and unspecified)')

        # Check for the array-like metadata
        for datatype in Dap._array_meta:
            ok, bads = self._arevalid(datatype)
            if not ok:
                if not bads:
                    self._report_problem(datatype + ' is not a valid non-empty list')
                else:
                    for bad in bads:
                        self._report_problem(bad + ' in ' + datatype +
                            ' is not valid or is a duplicate')

        # Check that there is no unknown metadata
        leftovers = set(self.meta.keys()) - (Dap._required_meta | Dap._optional_meta)
        if leftovers:
            self._report_problem('Unknown metadata: ' + str(leftovers))

    def _check_topdir(self):
        '''Check that everything is in correct top-level directory
         Only call this from check()'''
        dirname = os.path.dirname(self._meta_location)
        if not dirname:
            self._report_problem('mata.yaml is not in top-level directory')
        else:
            for path in self.files:
                if not path.startswith(dirname):
                    self._report_problem(path + ' is outside of ' + dirname +
                        ' top-level directory')
        if self.meta['package_name'] and self.meta['version']:
            desired_dirname = self.meta['package_name'] + '-' + self.meta['version']
            desired_filename = desired_dirname + '.dap'
            if dirname and dirname != desired_dirname:
                self._report_problem('Top-level directory with meta.yaml is not named ' +
                    desired_dirname)
            if self.basename != desired_filename:
                self._report_problem('The dap filename is not ' + desired_filename)

    def _is_dir(self, f):
        '''Check if the given in-dap file is a directory'''
        return self._tar.getmember(f).type == tarfile.DIRTYPE

    def _get_emptydirs(self, files):
        '''Find empty directories and return them
        Only works for actual files in dap'''
        emptydirs = []
        for f in files:
            if self._is_dir(f):
                empty = True
                for ff in files:
                    if ff.startswith(f + '/'):
                        empty = False
                        break
                if empty:
                    emptydirs.append(f)
        return emptydirs

    def _check_selfdeps(self, report=True):
        '''Check that the package does not depend on itself'''
        if self.meta['package_name'] and self.meta['dependencies']:
            dependencies = set()
            for dependency in self.meta['dependencies']:
                try:
                    if dependency in self._badmeta['dependencies']:
                        continue
                except (KeyError, AttributeError):
                    pass
                for mark in '== >= <= < >'.split():
                    dep = dependency.split(mark)
                    if len(dep) == 2:
                        dependencies.add(dep[0].strip())
                        break
            if self.meta['package_name'] in dependencies:
                if report:
                    self._report_problem('Depends on dap with the same name as itself')
                return False
        return True

    def _check_dapi(self):
        '''Check that the package_name is not registered on Dapi'''
        if self.meta['package_name']:
            from . import dapicli
            d = dapicli.metadap(self.meta['package_name'])
            if d:
                self._report_problem('This dap name is already registered on Dapi',
                    logging.WARNING)

    def _check_files(self):
        '''Check that there are only those files the standard accepts'''
        dirname = os.path.dirname(self._meta_location)

        if dirname:
            dirname += '/'
        files = [f for f in self.files if f.startswith(dirname)]
        if len(files) == 1:
            self._report_problem('Only meta.yaml in dap', logging.WARNING)
            return

        files.remove(dirname + 'meta.yaml')

        # Report and remove empty directories until no more are found
        emptydirs = self._get_emptydirs(files)
        while emptydirs:
            for ed in emptydirs:
                self._report_problem(ed + ' is empty directory (may be nested)', logging.WARNING)
                files.remove(ed)
            emptydirs = self._get_emptydirs(files)

        if self.meta['package_name']:
            name = self.meta['package_name']

            dirs = re.compile('^' + dirname + '((assistants(/(crt|twk|prep|extra))?|snippets)(/' +
                              name + ')?|icons(/(crt|twk|prep|extra|snippets)(/' + name +
                              ')?)?|files|(files/(crt|twk|prep|extra|snippets)|doc)(/' + name +
                              '(/.+)?)?)$')
            regs = re.compile('^' + dirname + '((assistants(/(crt|twk|prep|extra))|snippets)/' +
                              name + r'(/[^/]+)?\.yaml|icons/(crt|twk|prep|extra|snippets)/' +
                              name + r'(/[^/]+)?\.(' + Dap._icons +
                              ')|(files/(crt|twk|prep|extra|snippets)|doc)/' + name + '/.+)$')

            remove = []
            for f in files:
                if self._is_dir(f) and not dirs.match(f):
                    self._report_problem(f + '/ is not allowed directory')
                    remove.append(f)
                elif not self._is_dir(f) and not regs.match(f):
                    self._report_problem(f + ' is not allowed file')
                    remove.append(f)
            for r in remove:
                files.remove(r)

            # Subdir yamls need a chief
            for directory in ['assistants/' + t for t in 'crt twk prep extra'.split()] + \
                    ['snippets']:
                prefix = dirname + directory + '/'
                for f in files:
                    if f.startswith(prefix) and self._is_dir(f) and f + '.yaml' not in files:
                        self._report_problem(f + '/ present, but ' + f + '.yaml missing')

        # Let's warn about icons
        icons = []          # we need to report duplicates
        assistants = set()  # duplicates are fine here
        for f in files:
            if not self._is_dir(f):
                if f.startswith(os.path.join(dirname, 'icons/')):
                    # name without extension and dirname/icons/
                    icons.append('.'.join(f[len(os.path.join(dirname, 'icons/')):].
                        split('.')[:-1]))
                if f.startswith(os.path.join(dirname, 'assistants/')):
                    # extension is .yaml only, so we don't need to split and join
                    assistants.add(f[len(os.path.join(dirname, 'assistants/')):-len('.yaml')])
        duplicates = set([x for x in icons if icons.count(x) > 1])
        for d in duplicates:
            self._report_problem('Duplicate icon for ' + f, logging.WARNING)
        icons = set(icons)
        for i in icons - assistants:
            self._report_problem('Useless icon for non-exisiting assistant ' + i, logging.WARNING)
        for a in assistants - icons:
            self._report_problem('Missing icon for assistant ' + a, logging.WARNING)

        # And also about files
        folders = set()
        # we cannot reuse the one form icons, as we need to record the type as well
        assistants = set()
        for f in files:
            if self._is_dir(f):
                if f.startswith(os.path.join(dirname, 'files/')):
                    name = f[len(os.path.join(dirname, 'files/')):]
                    # name is crt/foo/bah/eggs
                    name = '/'.join(name.split('/')[:2])
                    # name is crt/foo
                    folders.add(name)
            else:
                for t in 'crt twk prep extra'.split():
                    if f.startswith(os.path.join(dirname, 'assistants', t, '')):
                        # extension is .yaml only, so we don't need to split
                        assistants.add(f[len(os.path.join(dirname, 'assistants/')):-len('.yaml')])
                if f.startswith(os.path.join(dirname, 'snippets/')):
                    assistants.add(f[len(os.path.join(dirname, '')):-len('.yaml')])
        folders -= set('crt twk prep extra snippets'.split())
        for f in folders - assistants:
            self._report_problem('Useless files for non-exisiting assistant ' + f, logging.WARNING)

    def check(self, network=False, raises=False, logger=logger):
        '''Checks if the dap is valid, reports problems

        Parameters:
            network -- whether to run checks that requires network connection
            output -- where to write() problems, might be None
            raises -- whether to raise an exception immediately after problem is detected'''
        self._check_raises = raises
        self._problematic = False
        self._logger = logger

        self._check_meta()
        self._check_selfdeps()
        self._check_topdir()
        self._check_files()

        if network:
            self._check_dapi()

        del self._check_raises
        return not self._problematic

    def extract(self, location):
        '''Extract the contents of a dap to a given location'''
        self._tar.extractall(location)

    def list_assistants(self):
        '''Lists assistants and snippets contained in the dap.
        Assumes the dap is valid (i.e. it has already been checked).'''
        # Remove the first directory from the paths
        stripped = map(lambda f: '/'.join(f.split('/')[1:]), self.files)
        # Only return matching paths (but without the .yaml at the end)
        return [f[:-5] for f in stripped if Dap._assistants.match(f)]
