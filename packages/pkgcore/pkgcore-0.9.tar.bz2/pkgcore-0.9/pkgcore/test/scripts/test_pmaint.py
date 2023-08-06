# Copyright: 2006-2011 Brian Harring <ferringb@gmail.com>
# Copyright: 2006 Marien Zwart <marienz@gentoo.org>: BSD/GPL2
# License: BSD/GPL2

from functools import partial

from snakeoil import compatibility
from snakeoil.formatters import PlainTextFormatter
from snakeoil.mappings import AttrAccessible

from pkgcore.config import basics, ConfigHint, configurable
from pkgcore.ebuild.cpv import CPV
from pkgcore.operations.repo import install, uninstall, replace, operations
from pkgcore.repository import util, syncable
from pkgcore.scripts import pmaint
from pkgcore.sync import base
from pkgcore.test import TestCase
from pkgcore.test.scripts import helpers

if compatibility.is_py3k:
    from io import BytesIO
else:
    from StringIO import StringIO as BytesIO


Options = AttrAccessible


class FakeSyncer(base.syncer):

    def __init__(self,  *args, **kwargs):
        self.succeed = kwargs.pop('succeed', True)
        base.syncer.__init__(self, *args, **kwargs)
        self.synced = False

    def _sync(self, verbosity, output_fd, **kwds):
        self.synced = True
        return self.succeed


class SyncableRepo(syncable.tree, util.SimpleTree):

    pkgcore_config_type = ConfigHint(typename='raw_repo')

    def __init__(self, succeed=True):
        util.SimpleTree.__init__(self, {})
        syncer = FakeSyncer('/fake', 'fake', succeed=succeed)
        syncable.tree.__init__(self, syncer)


success_section = basics.HardCodedConfigSection({'class': SyncableRepo,
                                                 'succeed': True})
failure_section = basics.HardCodedConfigSection({'class': SyncableRepo,
                                                 'succeed': False})


class TestSync(TestCase, helpers.ArgParseMixin):

    _argparser = pmaint.sync

    def test_parser(self):
        values = self.parse(repo=success_section)
        self.assertEqual(['repo'], [x[0] for x in values.repos])
        values = self.parse('repo', repo=success_section)
        self.assertEqual(['repo'], [x[0] for x in values.repos])

    def test_sync(self):
        config = self.assertOut(
            [
                "*** syncing 'myrepo'...",
                "*** synced 'myrepo'",
                ],
            myrepo=success_section)
        self.assertTrue(config.raw_repo['myrepo']._syncer.synced)
        self.assertOut(
            [
                "*** syncing 'myrepo'...",
                "*** failed syncing 'myrepo'",
                ],
            myrepo=failure_section)
        self.assertOutAndErr(
            [
                "*** syncing 'goodrepo'...",
                "*** synced 'goodrepo'",
                "*** syncing 'badrepo'...",
                "*** failed syncing 'badrepo'",
                "*** synced 'goodrepo'",
                ], [
                "!!! failed sync'ing 'badrepo'",
                ],
            'goodrepo', 'badrepo',
            goodrepo=success_section, badrepo=failure_section)


class fake_pkg(CPV):

    def __init__(self, repo, *a, **kw):
        CPV.__init__(self, *a, **kw)
        object.__setattr__(self, 'repo', repo)

def derive_op(name, op, *a, **kw):
    if isinstance(name, basestring):
        name = [name]
    name = ['finalize_data'] + list(name)
    class new_op(op):
        def f(*a, **kw):
            return True
        for x in name:
            locals()[x] = f
        del f, x

    return new_op(*a, **kw)


class fake_operations(operations):

    def _cmd_implementation_install(self, pkg, observer):
        self.repo.installed.append(pkg)
        return derive_op('add_data', install, self.repo, pkg, observer)

    def _cmd_implementation_uninstall(self, pkg, observer):
        self.repo.uninstalled.append(pkg)
        return derive_op('remove_data', uninstall, self.repo, pkg, observer)

    def _cmd_implementation_replace(self, oldpkg, newpkg, observer):
        self.repo.replaced.append((oldpkg, newpkg))
        return derive_op(('add_data', 'remove_data'),
            replace, self.repo, oldpkg, newpkg, observer)


class fake_repo(util.SimpleTree):

    operations_kls = fake_operations

    def __init__(self, data, frozen=False, livefs=False):
        self.installed = []
        self.replaced = []
        self.uninstalled = []
        util.SimpleTree.__init__(self, data,
            pkg_klass=partial(fake_pkg, self))
        self.livefs = livefs
        self.frozen = frozen


def make_repo_config(repo_data, livefs=False, frozen=False):
    def repo():
        return fake_repo(repo_data, livefs=livefs, frozen=frozen)
    repo.pkgcore_config_type = ConfigHint(typename='repo')
    return basics.HardCodedConfigSection({'class':repo})


class TestCopy(TestCase, helpers.ArgParseMixin):

    _argparser = pmaint.copy

    def execute_main(self, *a, **kw):
        config = self.parse(*a, **kw)
        out = PlainTextFormatter(BytesIO())
        ret = config.main_func(config, out, out)
        return ret, config, out

    def test_normal_function(self):
        ret, config, out = self.execute_main(
            'trg', '--source-repo', 'src',
            '*',
                src=make_repo_config({'sys-apps':{'portage':['2.1', '2.3']}}),
                trg=make_repo_config({})
            )
        self.assertEqual(ret, 0, "expected non zero exit code")
        self.assertEqual(map(str, config.target_repo.installed),
            ['sys-apps/portage-2.1', 'sys-apps/portage-2.3'])
        self.assertEqual(config.target_repo.uninstalled,
            config.target_repo.replaced,
            msg="uninstalled should be the same as replaced; empty")

        d = {'sys-apps':{'portage':['2.1', '2.2']}}
        ret, config, out = self.execute_main(
            'trg', '--source-repo', 'src',
            '=sys-apps/portage-2.1',
                src=make_repo_config(d),
                trg=make_repo_config(d)
            )
        self.assertEqual(ret, 0, "expected non zero exit code")
        self.assertEqual([map(str, x) for x in config.target_repo.replaced],
            [['sys-apps/portage-2.1', 'sys-apps/portage-2.1']])
        self.assertEqual(config.target_repo.uninstalled,
            config.target_repo.installed,
            msg="installed should be the same as uninstalled; empty")

    def test_ignore_existing(self):
        ret, config, out = self.execute_main(
            'trg', '--source-repo', 'src',
            '*', '--ignore-existing',
                src=make_repo_config({'sys-apps':{'portage':['2.1', '2.3']}}),
                trg=make_repo_config({})
            )
        self.assertEqual(ret, 0, "expected non zero exit code")
        self.assertEqual(map(str, config.target_repo.installed),
            ['sys-apps/portage-2.1', 'sys-apps/portage-2.3'])
        self.assertEqual(config.target_repo.uninstalled,
            config.target_repo.replaced,
            msg="uninstalled should be the same as replaced; empty")

        ret, config, out = self.execute_main(
            'trg', '--source-repo', 'src',
            '*', '--ignore-existing',
                src=make_repo_config({'sys-apps':{'portage':['2.1', '2.3']}}),
                trg=make_repo_config({'sys-apps':{'portage':['2.1']}})
            )
        self.assertEqual(ret, 0, "expected non zero exit code")
        self.assertEqual(map(str, config.target_repo.installed),
            ['sys-apps/portage-2.3'])
        self.assertEqual(config.target_repo.uninstalled,
            config.target_repo.replaced,
            msg="uninstalled should be the same as replaced; empty")


class TestRegen(TestCase, helpers.ArgParseMixin):

    _argparser = pmaint.regen

    def test_parser(self):

        class TestSimpleTree(util.SimpleTree):
            pass

        @configurable(typename='repo')
        def fake_repo():
            return TestSimpleTree({})


        options = self.parse(
            'spork', '--threads', '2', spork=basics.HardCodedConfigSection(
                {'class': fake_repo}))
        self.assertEqual(
            [options.repo.__class__, options.threads],
            [TestSimpleTree, 2])
