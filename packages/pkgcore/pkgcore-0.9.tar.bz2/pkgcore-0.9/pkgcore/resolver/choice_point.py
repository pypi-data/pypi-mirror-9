# Copyright: 2006-2010 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

__all__ = ("choice_point",)

from snakeoil import klass
from snakeoil.lists import iter_stable_unique


class choice_point(object):

    __slots__ = (
        "__weakref__", "atom", "matches", "matches_cur", "solution_filters",
        "_prdeps", "_rdeps", "_deps")

    def __init__(self, a, matches):
        self.atom = a
        self.matches = iter(matches)
        self.matches_cur = None
        self.solution_filters = set()
        # match solutions, remaining
        self._deps = None
        self._rdeps = None
        self._prdeps = None

    @property
    def state(self):
        """Return choice point state.

        :return: A tuple consisting of the number of possible choices,
            current matches' repo, current package match, all possible
            matches, build deps, runtime deps, and post merge deps.
        """
        m = self.matches_cur
        return (len(self.solution_filters),
            m.repo, m,
            self.matches,
            self._deps,
            self._rdeps,
            self._prdeps)

    @staticmethod
    def _filter_choices(cnf_reqs, filterset):
        for choices in cnf_reqs:
            l = [x for x in choices if x not in filterset]
            if not l:
                return
            yield l

    def _internal_force_next(self):
        """Force next pkg without triggering a reduce_atoms call.

        :return: True if pkgs remain, False if no more remain
        """
        for self.matches_cur in self.matches:
            self._reset_iters()
            return True
        self.matches_cur = self.matches = None
        return False

    def reduce_atoms(self, atom):
        """Alter choice point atom set.

        :param atom: set of package atoms
        :type atom: set of :obj:`pkgcore.ebuild.atom.atom`
        :return: True if no more pkgs remain or atoms were removed,
            False if no atoms were removed
        """
        if self.matches is None:
            raise IndexError("no solutions remain")
        if hasattr(atom, "__contains__") and not isinstance(atom, basestring):
            self.solution_filters.update(atom)
        else:
            self.solution_filters.add(atom)

        filterset = self.solution_filters
        if self.matches_cur is None:
            if not self._internal_force_next():
                return True

        round = -1
        while True:
            round += 1
            if round:
                if not self._internal_force_next():
                    return True

            for depset_name in ("_deps", "_rdeps", "_prdeps"):
                depset = getattr(self, depset_name)
                reqs = list(self._filter_choices(depset, filterset))
                if len(reqs) != len(depset):
                    break
                setattr(self, depset_name, reqs)
            else:
                return round > 0

    def _reset_iters(self):
        """
        Reset depends, rdepends, and post_rdepends properties
        to current matches' related attributes.
        """
        cur = self.matches_cur
        self._deps = cur.depends.cnf_solutions()
        self._rdeps = cur.rdepends.cnf_solutions()
        self._prdeps = cur.post_rdepends.cnf_solutions()

    slot = klass.alias_attr("current_pkg.slot")
    key = klass.alias_attr("current_pkg.key")

    @property
    def current_pkg(self):
        """Current selected package."""
        if self.matches_cur is None:
            if self.matches is None:
                raise IndexError("no packages remain")
            for self.matches_cur in self.matches:
                break
            else:
                self.matches = None
                raise IndexError("no more packages remain")
            self._reset_iters()
        return self.matches_cur

    def force_next_pkg(self):
        """Force next package to be selected from available matches."""
        if self.matches is None:
            return False
        for self.matches_cur in self.matches:
            break
        else:
            self.matches_cur = self.matches = None
            return False
        return self.reduce_atoms([])

    @property
    def depends(self):
        """Build time dependencies."""
        if not self:
            raise IndexError("no more solutions remain")
        return self._deps

    @property
    def rdepends(self):
        """Runtime dependencies."""
        if not self:
            raise IndexError("no more solutions remain")
        return self._rdeps

    @property
    def post_rdepends(self):
        """Post merge dependencies."""
        if not self:
            raise IndexError("no more solutions remain")
        return self._prdeps

    def __nonzero__(self):
        if self.matches_cur is None:
            if self.matches is None:
                return False
            for self.matches_cur in self.matches:
                break
            else:
                self.matches = None
                return False
            self._reset_iters()
        return True

    def __str__(self):
        return "%s: (%s, %s)" % (self.__class__.__name__,
            self.atom, self.matches_cur)
