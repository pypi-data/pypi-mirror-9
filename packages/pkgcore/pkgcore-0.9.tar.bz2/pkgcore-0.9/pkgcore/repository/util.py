# Copyright: 2006-2011 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

__all__ = ("SimpleTree", "RepositoryGroup")

from snakeoil import klass
from snakeoil.demandload import demandload

from pkgcore.ebuild.cpv import versioned_CPV
from pkgcore.repository.prototype import tree

demandload(
    "pkgcore.repository:multiplex",
)


class SimpleTree(tree):

    def __init__(self, cpv_dict, pkg_klass=None, livefs=False, frozen=True,
                 repo_id=None):
        self.cpv_dict = cpv_dict
        if pkg_klass is None:
            pkg_klass = versioned_CPV
        self.livefs = livefs
        self.repo_id = repo_id
        self.package_class = pkg_klass
        tree.__init__(self, frozen=frozen)

    def _get_categories(self, *arg):
        if arg:
            return ()
        return tuple(self.cpv_dict.iterkeys())

    def _get_packages(self, category):
        return tuple(self.cpv_dict[category].iterkeys())

    def _get_versions(self, cp_key):
        return tuple(self.cpv_dict[cp_key[0]][cp_key[1]])

    def notify_remove_package(self, pkg):
        vers = self.cpv_dict[pkg.category][pkg.package]
        vers = [x for x in vers if x != pkg.fullver]
        if vers:
            self.cpv_dict[pkg.category][pkg.package] = vers
        else:
            del self.cpv_dict[pkg.category][pkg.package]
            if not self.cpv_dict[pkg.category]:
                del self.cpv_dict[pkg.category]
        tree.notify_remove_package(self, pkg)

    def notify_add_package(self, pkg):
        self.cpv_dict.setdefault(pkg.category,
            {}).setdefault(pkg.package, []).append(pkg.fullver)
        tree.notify_add_package(self, pkg)


class RepositoryGroup(object):

    def __init__(self, repositories, combined=None):
        self.repositories = tuple(repositories)
        if combined is None:
            if len(self.repositories) == 1:
                combined = self.repositories[0]
            else:
                combined = multiplex.tree(*self.repositories)
        self.combined = combined

    itermatch = klass.alias_attr("combined.itermatch")
    has_match = klass.alias_attr("combined.has_match")
    match = klass.alias_attr("combined.match")

    def __iter__(self):
        return iter(self.repositories)

    @classmethod
    def change_repos(cls, repositories):
        return cls(repositories)
