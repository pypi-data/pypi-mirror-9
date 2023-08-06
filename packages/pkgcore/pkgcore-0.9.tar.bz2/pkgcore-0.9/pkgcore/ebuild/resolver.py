# Copyright: 2006-2011 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

"""
resolver configuration to match portage behaviour (misbehaviour in a few spots)
"""

__all__ = ["upgrade_resolver", "min_install_resolver"]

from snakeoil.demandload import demandload

from pkgcore.repository import misc, multiplex
from pkgcore.resolver import plan

demandload(
    'pkgcore.restrictions:packages,values',
)


def upgrade_resolver(vdbs, dbs, verify_vdb=True, nodeps=False,
                     force_replace=False, resolver_cls=plan.merge_plan,
                     **kwds):

    """
    generate and configure a resolver for upgrading all processed nodes.

    :param vdbs: list of :obj:`pkgcore.repository.prototype.tree` instances
        that represents the livefs
    :param dbs: list of :obj:`pkgcore.repository.prototype.tree` instances
        representing sources of pkgs
    :param verify_vdb: should we stop resolving once we hit the vdb,
        or do full resolution?
    :return: :obj:`pkgcore.resolver.plan.merge_plan` instance
    """

    f = plan.merge_plan.prefer_highest_version_strategy
    # hack.
    if nodeps:
        vdbs = map(misc.nodeps_repo, vdbs)
        dbs = map(misc.nodeps_repo, dbs)
    elif not verify_vdb:
        vdbs = map(misc.nodeps_repo, vdbs)
        dbs = list(dbs)

    if force_replace:
        resolver_cls = generate_replace_resolver_kls(resolver_cls)
    return resolver_cls(dbs + vdbs, plan.pkg_sort_highest, f, **kwds)


def min_install_resolver(vdbs, dbs, verify_vdb=True, nodeps=False,
                         force_replace=False, resolver_cls=plan.merge_plan,
                         **kwds):
    """
    Resolver that tries to minimize the number of changes while installing.

    generate and configure a resolver that is focused on just
    installing requests- installs highest version it can build a
    solution for, but tries to avoid building anything not needed

    :param vdbs: list of :obj:`pkgcore.repository.prototype.tree` instances
        that represents the livefs
    :param dbs: list of :obj:`pkgcore.repository.prototype.tree` instances
        representing sources of pkgs
    :param verify_vdb: should we stop resolving once we hit the vdb,
        or do full resolution?
    :return: :obj:`pkgcore.resolver.plan.merge_plan` instance
    """

    if nodeps:
        vdbs = map(misc.nodeps_repo, vdbs)
        dbs = map(misc.nodeps_repo, dbs)
    elif not verify_vdb:
        vdbs = map(misc.nodeps_repo, vdbs)
        dbs = list(dbs)

    if force_replace:
        resolver_cls = generate_replace_resolver_kls(resolver_cls)
    return resolver_cls(vdbs + dbs, plan.pkg_sort_highest,
                        plan.merge_plan.prefer_reuse_strategy, **kwds)

_vdb_restrict = packages.OrRestriction(
    packages.PackageRestriction("repo.livefs", values.EqualityMatch(False)),
    packages.AndRestriction(
        packages.PackageRestriction(
            "category", values.StrExactMatch("virtual")),
        packages.PackageRestriction(
            "package_is_real", values.EqualityMatch(False)),
        ),
    )


class empty_tree_merge_plan(plan.merge_plan):

    _vdb_restriction = _vdb_restrict

    def __init__(self, dbs, *args, **kwds):
        """
        :param args: see :obj:`pkgcore.resolver.plan.merge_plan.__init__`
            for valid args
        :param kwds: see :obj:`pkgcore.resolver.plan.merge_plan.__init__`
            for valid args
        """
        plan.merge_plan.__init__(self, dbs, *args, **kwds)
        # XXX *cough*, hack.
        self.default_dbs = multiplex.tree(
            *[x for x in self.all_raw_dbs if not x.livefs])


def generate_replace_resolver_kls(resolver_kls):

    class replace_resolver(resolver_kls):
        overriding_resolver_kls = resolver_kls
        _vdb_restriction = _vdb_restrict

        def add_atoms(self, restricts, **kwds):
            restricts = [packages.KeyedAndRestriction(self._vdb_restriction, x, key=x.key)
                         for x in restricts]
            return self.overriding_resolver_kls.add_atoms(self, restricts, **kwds)

    return replace_resolver
