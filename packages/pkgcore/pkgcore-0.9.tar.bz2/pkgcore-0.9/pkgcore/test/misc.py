# Copyright: 2007-2011 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

# misc things useful for tests.

from itertools import ifilter, imap

from snakeoil.mappings import AttrAccessible

from pkgcore import plugin
from pkgcore.ebuild.atom import atom
from pkgcore.ebuild.conditionals import DepSet
from pkgcore.ebuild.cpv import CPV
from pkgcore.ebuild.eapi import get_eapi
from pkgcore.ebuild.ebuild_src import package
from pkgcore.ebuild.misc import collapsed_restrict_to_data
from pkgcore.package.metadata import factory
from pkgcore.repository.util import SimpleTree
from pkgcore.restrictions.packages import AlwaysTrue

default_arches = set(["x86", "ppc", "amd64", "ia64"])

Options = AttrAccessible


class FakePkgBase(package):

    __slots__ = ()

    def __init__(self, cpvstr, data=None, shared=None, repo=None):
        if data is None:
            data = {}

        for x in ("DEPEND", "RDEPEND", "PDEPEND", "IUSE", "LICENSE"):
            data.setdefault(x, "")

        data.setdefault("KEYWORDS", ' '.join(default_arches))

        cpv = CPV(cpvstr, versioned=True)
        package.__init__(self, shared, repo, cpv.category, cpv.package,
            cpv.fullver)
        object.__setattr__(self, "data", data)


class FakeProfile(object):

    def __init__(self, masked_use={}, forced_use={},
        provides={}, masks=[], virtuals={}, arch='x86', name='none'):
        self.provides_repo = SimpleTree(provides)
        self.masked_use = {atom(k): v for k,v in masked_use.iteritems()}
        self.forced_use = {atom(k): v for k,v in forced_use.iteritems()}
        self.masks = tuple(map(atom, masks))
        self.virtuals = SimpleTree(virtuals)
        self.arch = arch
        self.name = name

        self.forced_data = collapsed_restrict_to_data(
            [(AlwaysTrue, (self.arch,))],
            self.forced_use.iteritems())

        self.masked_data = collapsed_restrict_to_data(
            [(AlwaysTrue, default_arches)],
            self.masked_use.iteritems())

    def make_virtuals_repo(self, repo):
        return self.virtuals


class FakeRepo(object):

    def __init__(self, pkgs=(), repo_id='', location='', masks=(), **kwds):
        self.pkgs = pkgs
        self.repo_id = repo_id or location
        self.location = location
        self.default_visibility_limiters = masks

        for k, v in kwds.iteritems():
            setattr(self, k, v)

    def itermatch(self, restrict, sorter=iter, pkg_klass_override=lambda x:x):
        return ifilter(restrict.match,
            imap(pkg_klass_override, sorter(self.pkgs)))

    def match(self, restrict, **kwargs):
        return list(self.itermatch(restrict, **kwargs))


class FakePkg(FakePkgBase):
    def __init__(self, cpv, eapi="0", slot="0", subslot=None, iuse=(), use=(),
                 repo=FakeRepo(), restrict='', keywords=None):
        if isinstance(repo, str):
            repo = FakeRepo(repo)
        elif isinstance(repo, (tuple, list)) and len(repo) < 3:
            repo = FakeRepo(*repo)
        FakePkgBase.__init__(self, cpv, repo=factory(repo))
        if keywords is not None:
            object.__setattr__(self, "keywords", set(keywords))
        object.__setattr__(self, "slot", str(slot))
        if subslot is None:
            subslot = slot
        object.__setattr__(self, "subslot", subslot)
        object.__setattr__(self, "restrict", DepSet.parse(restrict, str))
        object.__setattr__(self, "fetchables", [])
        object.__setattr__(self, "use", set(use))
        object.__setattr__(self, "iuse", set(iuse))
        object.__setattr__(self, 'eapi_obj', get_eapi(eapi, False))


class DisablePlugins(object):

    default_state = {}
    wipe_plugin_state = True

    def force_plugin_state(self, wipe=True, **packages):
        if wipe:
            plugin._cache.clear()
        plugin._cache.update(packages)

    def setUp(self):
        self._plugin_orig_initialize = plugin.initialize_cache
        self._plugin_orig_cache = plugin._cache.copy()
        if self.wipe_plugin_state:
            plugin._cache = {}
        plugin.initialize_cache = lambda p:()

    def tearDown(self):
        plugin._cache = self._plugin_orig_cache
        plugin.initialize_cache = self._plugin_orig_initialize
