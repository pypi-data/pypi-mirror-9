# -*- coding: utf-8 -*-
import pytest
import sys
import os
import logging
import itertools
import glob
import subprocess
try:
    from cStringIO import StringIO
except:
    try:
        from StringIO import StringIO
    except:
        from io import StringIO
from devassistant.dapi import *
from test import fixtures_dir

def dap_path(fixture):
    '''Return appropriate dap path'''
    return os.path.join(fixtures_dir, 'dapi', 'daps', fixture)

def l(level = logging.WARNING, output = sys.stderr):
    '''Gets the logger'''
    logger = logging.getLogger('daptest')
    handler = logging.StreamHandler(output)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


class TestDap(object):
    '''Tests for the Dap class'''
    def test_no_gz(self):
        '''Not-gzip archive should raise DapFileError'''
        with pytest.raises(DapFileError):
            Dap(dap_path('bz2.dap'))

    def test_no_exist(self):
        '''Nonexisting file should raise DapFileError'''
        with pytest.raises(DapFileError):
            Dap('foo')

    def test_no_meta(self):
        '''Dap without meta.yaml should raise DapMetaError'''
        with pytest.raises(DapMetaError):
            Dap(dap_path('no_meta.dap'))

    def test_dap_data(self):
        '''Dap should have correct content in meta, basename and files'''
        dap = Dap(dap_path('meta_only/foo-1.0.0.dap'))
        assert dap.meta['package_name'] == 'foo'
        assert dap.meta['version'] == '1.0.0'
        assert u'Hrončok' in dap.meta['authors'][0]
        assert dap.basename == 'foo-1.0.0.dap'
        assert dap.files == ['foo-1.0.0', 'foo-1.0.0/meta.yaml']

    def test_no_toplevel(self):
        '''Dap with no top-level directory is invalid'''
        out = StringIO()
        assert not Dap(dap_path('no_toplevel/foo-1.0.0.dap')).check(logger=l(output=out, level=logging.ERROR))
        assert len(out.getvalue().rstrip().split('\n')) == 1
        assert 'not in top-level directory' in out.getvalue()

    def test_valid_names(self):
        '''Test if valid names are valid'''
        d = Dap('', fake=True)
        for name in 'foo f bar v8 foo-bar-foo ffffff8ff f-_--s '.split():
            d.meta['package_name'] = name
            assert d._isvalid('package_name')

    def test_invalid_names(self):
        '''Test if invalid names are invalid'''
        d = Dap('', fake=True)
        for name in '9 8f -a - a_ _ ř H aaHa ? aa!a () * ff+a f8-- .'.split():
            d.meta['package_name'] = name
            assert not d._isvalid('package_name')

    def test_valid_versions(self):
        '''Test if valid versions are valid'''
        d = Dap('', fake=True)
        for version in '0 1 888 0.1 0.1a 0.0.0b 666dev 0.0.0.0.0 8.11'.split():
            d.meta['version'] = version
            assert d._isvalid('version')

    def test_invalid_versions(self):
        '''Test if invalid versions are invalid'''
        d = Dap('', fake=True)
        for version in '00 01 0.00.0 01.0 1c .1 1-2 h č . 1..0 1.0.'.split():
            d.meta['version'] = version
            assert not d._isvalid('version')

    def test_loading_float_version(self):
        '''Test that loading doesn't fail if version is loaded from YAML as float'''
        out = StringIO()
        assert Dap(dap_path('meta_only/bad_version-0.1.dap')).check(logger=l(output=out, level=logging.ERROR))

    def test_valid_urls(self):
        '''Test if valid URLs are valid'''
        d = Dap('', fake=True)
        urls = ['http://g.com/aa?ff=g&g#f',
                'ftp://g.aa/',
                'http://user:password@fee.com',
                'https://f.f.f.f.f.sk/cgi-bin/?f=Program%20Files']
        for url in urls:
            d.meta['homepage'] = url
            assert d._isvalid('homepage')

    def test_invalid_urls(self):
        '''Test if invalid URLs are invalid'''
        d = Dap('', fake=True)
        urls = ['g.com/a',
                'mailto:foo@bar.com',
                'ftp://192.168.1.1/?a',
                'https://localhost/']
        for url in urls:
            d.meta['homepage'] = url
            assert not d._isvalid('homepage')

    def test_valid_bugreports(self):
        '''Test if valid URLs or e-mails are valid'''
        d = Dap('', fake=True)
        bugs = ['http://g.com/',
                'miro@hroncok.cz',
                '?ouch@devassiatnt.org',
                'par_at_no.id',
                'par_at_n@o.id']
        for bug in bugs:
            d.meta['bugreports'] = bug
            assert d._isvalid('bugreports')

    def test_invalid_bugreports(self):
        '''Test if invalid URLs or e-mails are invalid'''
        d = Dap('', fake=True)
        bugs = ['httpr://g.com/',
                'miro@h@roncok.cz',
                '?ouchdevassiatnt.org',
                'par_at_no.iduss',
                '@o.id']
        for bug in bugs:
            d.meta['bugreports'] = bug
            assert not d._isvalid('bugreports')

    def test_valid_summary(self):
        '''Test if valid summary is valid'''
        d = Dap('', fake=True)
        d.meta['summary'] = 'foo'
        assert d._isvalid('summary')

    def test_invalid_summary(self):
        '''Test if invalid summary is invalid'''
        d = Dap('', fake=True)
        d.meta['summary'] = 'foo\nbar'
        assert not d._isvalid('summary')

    def test_empty_required(self):
        '''Required metadata should fail when undefined'''
        d = Dap('', fake=True)
        for item in 'package_name version license authors summary'.split():
            assert not d._isvalid(item)

    def test_valid_licenses(self):
        '''Test if valid licenses are valid'''
        d = Dap('', fake=True)
        licenses = ['AGPLv3 with exceptions',
                    'GPL+ or Artistic',
                    'LGPLv2+ and LGPLv2 and LGPLv3+ and (GPLv3 or LGPLv2) and (GPLv3+ or LGPLv2) and (CC-BY-SA or LGPLv2+) and (CC-BY-SA or LGPLv2) and CC-BY and BSD and MIT and Public Domain']
        for license in licenses:
            d.meta['license'] = license
            assert d._isvalid('license')

    def test_invalid_licenses(self):
        '''Test if invalid licenses are invalid'''
        d = Dap('', fake=True)
        licenses = ['Redistributable',
                    'GPLv4',
                    'LGPLv2+ and (LGPLv2',
                    'GNU GPL']
        for license in licenses:
            d.meta['license'] = license
            assert not d._isvalid('license')

    def test_valid_authors(self):
        '''Test if valid authors are valid'''
        d = Dap('', fake=True)
        pool = [u'Miro Hrončok <miro@hroncok.cz>',
                u'Miro Hrončok <miro_at_hroncok.cz>',
                u'Miro Hrončok',
                u'Dr. Voštěp',
                u'Никола I Петровић-Његош']
        for r in range(1, len(pool) + 1):
            for authors in itertools.combinations(pool, r):
                d.meta['authors'] = list(authors)
                ok, bads = d._arevalid('authors')
                assert ok
                assert not bads

    def test_invalid_authors(self):
        '''Test if invalid authors are invalid'''
        d = Dap('', fake=True)
        pool = [u'Miro Hrončok ',
                ' ',
                u' Miro Hrončok',
                u'Miro Hrončok miro@hroncok.cz',
                u'Miro Hrončok <miro@hr@oncok.cz>',
                '']
        for r in range(1, len(pool) + 1):
            for authors in itertools.combinations(pool, r):
                d.meta['authors'] = list(authors)
                ok, bads = d._arevalid('authors')
                assert not ok
                assert bads == list(authors)
        d.meta['authors'] = ['OK2 <ok@ok.ok>'] + pool + ['OK <ok@ok.ok>']
        ok, bads = d._arevalid('authors')
        assert bads == pool

    def test_duplicate_authors(self):
        '''Test if duplicate valid authors are invalid'''
        d = Dap('', fake=True)
        d.meta['authors'] = ['A', 'B', 'A']
        ok, bads = d._arevalid('authors')
        assert not ok
        assert bads == ['A']

    def test_empty_authors(self):
        '''Test if empty authors list is invalid'''
        d = Dap('', fake=True)
        d.meta['authors'] = []
        ok, null = d._arevalid('authors')
        assert not ok

    def test_valid_dependencies(self):
        '''Test if valid dependencies are valid'''
        d = Dap('', fake=True)
        pool = ['foo',
                'foo == 1.0.0',
                'foo >= 1.0.0',
                'foo <= 1.0.0',
                'foo > 1.0.0',
                'foo  < 1.0.0',
                'foo <1.0.0',
                'foo<1.0.0',
                'foo< 1.0.0',
                'foo      <    1.0.0',
                'foo                   <1.0.0',
                'foo < 1.0.0b']
        for r in range(1, len(pool) + 1):
            for dependencies in itertools.combinations(pool, r):
                d.meta['dependencies'] = list(dependencies)
                ok, bads = d._arevalid('dependencies')
                assert ok
                assert not bads

    def test_invalid_dependencies(self):
        '''Test if invalid dependencies are invalid'''
        d = Dap('', fake=True)
        pool = ['foo != 1.0.0',
                'foo = 1.0.0',
                'foo =< 1.0.0',
                'foo >> 1.0.0',
                'foo > = 1.0.0',
                '1.0.0',
                'foo-1.0.0',
                ' ',
                '']
        for r in range(1, len(pool) + 1):
            for dependencies in itertools.combinations(pool, r):
                d.meta['dependencies'] = list(dependencies)
                ok, bads = d._arevalid('dependencies')
                assert not ok
                assert bads == list(dependencies)
        d.meta['dependencies'] = ['foo'] + pool + ['bar']
        ok, bads = d._arevalid('dependencies')
        assert bads == pool

    def test_duplicate_dependencies(self):
        '''Test if duplicate valid dependencies are invalid'''
        d = Dap('', fake=True)
        d.meta['dependencies'] = ['A', 'B', 'A']
        ok, bads = d._arevalid('dependencies')
        assert not ok
        assert bads == ['A']

    def test_self_dependency(self):
        '''Test if depending on itself produces error'''
        d = Dap('', fake=True)
        d.meta['dependencies'] = ['A', 'B > 1']
        d.meta['package_name'] = 'B'
        assert not d._check_selfdeps(report=False)

        d.meta['package_name'] = 'C'
        assert d._check_selfdeps(report=False)

        d.meta['dependencies'] = ['C', 'B=1', 'A']
        d.meta['package_name'] = 'B'
        d._arevalid('dependencies')
        assert d._check_selfdeps(report=False)

    def test_empty_dependencies(self):
        '''Test if empty dependencies list is valid'''
        d = Dap('', fake=True)
        d.meta['dependencies'] = []
        ok, null = d._arevalid('dependencies')
        assert ok

    def test_valid_supported_platforms(self):
        '''Test if valid supported_platforms are valid'''
        d = Dap('', fake=True)
        pool = ['suse',
                'debian',
                'fedora',
                'redhat',
                'centos',
                'mandrake',
                'mandriva',
                'rocks',
                'slackware',
                'yellowdog',
                'gentoo',
                'unitedlinux',
                'turbolinux',
                'arch',
                'mageia',
                'ubuntu',
                'darwin']
        for r in range(1, len(pool) + 1):
            for dependencies in itertools.combinations(pool, r):
                d.meta['supported_platforms'] = list(dependencies)
                ok, bads = d._arevalid('supported_platforms')
                assert ok
                assert not bads

    def test_invalid_supported_platforms(self):
        '''Test if invalid supported_platforms are invalid'''
        d = Dap('', fake=True)
        pool = ['linux', 'windows', '5', 'Mac OS X']
        for r in range(1, len(pool) + 1):
            for dependencies in itertools.combinations(pool, r):
                d.meta['supported_platforms'] = list(dependencies)
                ok, bads = d._arevalid('supported_platforms')
                assert not ok
                assert bads == list(dependencies)
        d.meta['supported_platforms'] = ['fedora'] + pool + ['darwin']
        ok, bads = d._arevalid('supported_platforms')
        assert bads == pool

    def test_duplicate_supported_platforms(self):
        '''Test if duplicate valid supported_platforms are invalid'''
        d = Dap('', fake=True)
        d.meta['supported_platforms'] = ['fedora', 'redhat', 'fedora']
        ok, bads = d._arevalid('supported_platforms')
        assert not ok
        assert bads == ['fedora']

    def test_empty_supported_platforms(self):
        '''Test if empty supported_platforms list is valid'''
        d = Dap('', fake=True)
        d.meta['supported_platforms'] = []
        ok, null = d._arevalid('supported_platforms')
        assert ok

    def test_meta_only_check(self):
        '''meta_only.dap should pass the test (errors only)'''
        dap = Dap(dap_path('meta_only/foo-1.0.0.dap'))
        assert dap.check(logger=l(level=logging.ERROR))

    def test_meta_only_warning_check(self):
        '''meta_only.dap shopuld produce warning'''
        out = StringIO()
        dap = Dap(dap_path('meta_only/foo-1.0.0.dap'))
        assert not dap.check(logger=l(output=out))
        assert len(out.getvalue().rstrip().split('\n')) == 1
        assert 'Only meta.yaml in dap' in out.getvalue()

    def test_unknown_metadata(self):
        '''meta_only.dap with added value should fail'''
        out = StringIO()
        dap = Dap(dap_path('meta_only/foo-1.0.0.dap'))
        dap.meta['foo'] = 'bar'
        assert not dap.check(logger=l(output=out, level=logging.ERROR))
        assert len(out.getvalue().rstrip().split('\n')) == 1
        assert 'Unknown metadata' in out.getvalue()
        assert 'foo' in out.getvalue()

    def test_forgotten_version_in_filename_and_dir(self):
        '''Dap without version in filename and dirname should produce 2 errors'''
        out = StringIO()
        assert not Dap(dap_path('meta_only/foo.dap')).check(logger=l(output=out, level=logging.ERROR))
        assert len(out.getvalue().rstrip().split('\n')) == 2
        assert 'Top-level directory with meta.yaml is not named foo-1.0.0' in out.getvalue()
        assert 'The dap filename is not foo-1.0.0.dap' in out.getvalue()

    def test_wrong_dap_filename(self):
        '''Dap with OK dirname, but wrong filename should produce 1 error'''
        out = StringIO()
        assert not Dap(dap_path('meta_only/bar.dap')).check(logger=l(output=out, level=logging.ERROR))
        assert len(out.getvalue().rstrip().split('\n')) == 1
        assert 'The dap filename is not foo-1.0.0.dap' in out.getvalue()

    def test_wrong_dap_filename_mimicked_to_be_ok(self):
        '''Dap with wrong filename, mimicked to be OK, should produce no error'''
        assert Dap(dap_path('meta_only/bar.dap'), mimic_filename='foo-1.0.0.dap').check(logger=l(level=logging.ERROR))

    def test_good_dap_filename_mimicked_to_be_wrong(self):
        '''Error passing dap, should fail with wrong mimicked filename'''
        assert not Dap(dap_path('meta_only/foo-1.0.0.dap'), mimic_filename='wrong').check(logger=l(level=logging.ERROR))

    def test_files_outside_of_toplevel_dir(self):
        '''Dap with files outside of top-level directory should produce error for each'''
        out = StringIO()
        assert not Dap(dap_path('outside_toplevel/foo-1.0.0.dap')).check(logger=l(output=out, level=logging.ERROR))
        assert len(out.getvalue().rstrip().split('\n')) == 3
        assert 'is outside' in out.getvalue()

    def test_empty_dirs(self):
        '''Dap with empty dirs produces warning'''
        out = StringIO()
        assert not Dap(dap_path('empty_dirs/foo-1.0.0.dap')).check(logger=l(output=out))
        assert len(out.getvalue().rstrip().split('\n')) == 3
        assert ' is empty directory' in out.getvalue()

    def test_wrong_files(self):
        '''Dap with wrong files produces errors'''
        out = StringIO()
        assert not Dap(dap_path('wrong_files/foo-1.0.0.dap')).check(logger=l(output=out, level=logging.ERROR))
        assert len(out.getvalue().rstrip().split('\n')) == 21
        assert '/files/wrong.txt is not allowed file' in out.getvalue()
        assert '/files/wrong/ is not allowed directory' in out.getvalue()
        assert '/files/wrong/a is not allowed file' in out.getvalue()
        assert '/files/foo/ is not allowed directory' in out.getvalue()
        assert '/files/foo/wrong is not allowed file' in out.getvalue()
        assert '/files/crt/wrong is not allowed file' in out.getvalue()
        assert '/icons/foo.gif is not allowed file' in out.getvalue()
        assert '/icons/foo.yaml is not allowed file' in out.getvalue()
        assert '/icons/twk/foo.gif is not allowed file' in out.getvalue()
        assert '/icons/twk/foo.yaml is not allowed file' in out.getvalue()
        assert '/icons/foo/ is not allowed directory' in out.getvalue()
        assert '/icons/foo/a.png is not allowed file' in out.getvalue()
        assert '/doc/README is not allowed file' in out.getvalue()
        assert '/snippets/bar/ is not allowed directory' in out.getvalue()
        assert '/snippets/bar/bar.yaml is not allowed file' in out.getvalue()
        assert '/assistants/wrong/ is not allowed directory' in out.getvalue()
        assert '/assistants/wrong/foo.yaml is not allowed file' in out.getvalue()
        assert '/assistants/extra/bar.txt is not allowed file' in out.getvalue()
        assert '/assistants/extra/bar.yaml is not allowed file' in out.getvalue()
        assert '/assistants/crt/test.yaml is not allowed file' in out.getvalue()
        assert '/assistants/prep/foo/ present' in out.getvalue()

    def test_icons_files_warnings(self):
        '''Dap with redundant or missing icons and redundant files should produce warnings'''
        out = StringIO()
        assert not Dap(dap_path('wrong_files/foo-1.0.0.dap')).check(logger=l(output=out))
        assert 'Useless icon for non-exisiting assistant twk/foo/a' in out.getvalue()
        assert 'Useless icon for non-exisiting assistant twk/foo/a' in out.getvalue()
        assert 'Useless icon for non-exisiting assistant crt/foo' in out.getvalue()
        assert 'Useless icon for non-exisiting assistant crt/foo' in out.getvalue()
        assert 'Missing icon for assistant twk/foo/bar' in out.getvalue()
        assert 'Missing icon for assistant twk/foo/bar' in out.getvalue()
        assert 'Missing icon for assistant prep/foo/bar' in out.getvalue()
        assert 'Missing icon for assistant prep/foo/bar' in out.getvalue()

    def test_dapi_check(self):
        '''Dap that is already on dapi should produce a warning when network is True'''
        out = StringIO()
        os.environ['DAPI_FAKE_DATA'] = 'nonempty'
        Dap(dap_path('meta_only/foo-1.0.0.dap')).check(logger=l(output=out), network=True)
        assert 'This dap name is already registered on Dapi' in out.getvalue()

    def test_dapi_check_false(self):
        '''Dap that is not already on dapi should not produce a warning when network is True'''
        out = StringIO()
        os.environ['DAPI_FAKE_DATA'] = ''
        Dap(dap_path('meta_only/foo-1.0.0.dap')).check(logger=l(output=out), network=True)
        assert 'This dap name is already registered on Dapi' not in out.getvalue()

    def test_dap_good_dependencies(self):
        '''Dap with good dependencies produces no error'''
        assert Dap(dap_path('dependencies/good-1.0.0.dap')).check(logger=l(level=logging.ERROR))

    def test_dap_invalid_dependencies(self):
        '''Dap with invalid dependency produces an error'''
        out = StringIO()
        assert not Dap(dap_path('dependencies/invalid-1.0.0.dap')).check(logger=l(output=out, level=logging.ERROR))
        assert 'invalid 0.0.1 in dependencies is not valid' in out.getvalue()

    def test_dap_self_dependenciey(self):
        '''Dap with self dependency produces an error'''
        out = StringIO()
        assert not Dap(dap_path('dependencies/self-1.0.0.dap')).check(logger=l(output=out, level=logging.ERROR))
        assert 'Depends on dap with the same name as itself' in out.getvalue()

    def test_sha256sum(self):
        '''Check that sha256sum of the files is the same as sha256sum command does'''
        for dap in glob.glob(dap_path('meta_only/*.dap')):
            process = subprocess.Popen(['sha256sum', dap], stdout=subprocess.PIPE)
            assert Dap(dap).sha256sum == process.communicate()[0].split()[0].decode('utf8')

    def test_list_assistants(self):
        '''Check that the list_assistants() method returns right results'''
        # Using set because we don't care about the order
        dapdap = set([
            'assistants/crt/dap',
            'assistants/twk/dap',
            'assistants/twk/dap/add',
            'assistants/twk/dap/pack',
            'snippets/dap',
        ])
        assert set(Dap(dap_path('list_assistants/dap-0.0.1a.dap')).list_assistants()) == dapdap
        assert Dap(dap_path('meta_only/foo-1.0.0.dap')).list_assistants() == []
