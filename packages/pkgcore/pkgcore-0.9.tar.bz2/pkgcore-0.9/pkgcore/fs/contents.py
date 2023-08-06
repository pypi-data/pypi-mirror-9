# Copyright: 2005-2011 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

"""
contents set- container of fs objects
"""

from functools import partial
from itertools import ifilter
from operator import attrgetter

from snakeoil.demandload import demandload
from snakeoil.klass import generic_equality, alias_method
from snakeoil.osutils import normpath, pjoin

from pkgcore.fs import fs

demandload(
    'collections:defaultdict',
    'os:path',
    'time',
    'snakeoil.mappings:OrderedDict',
)


def change_offset_rewriter(orig_offset, new_offset, iterable):
    path_sep = path.sep
    offset_len = len(orig_offset.rstrip(path_sep))
    # localize it.
    npf = normpath
    for x in iterable:
        # slip in the '/' default to force it to still generate a
        # full path still
        yield x.change_attributes(
            location=npf(pjoin(new_offset, x.location[offset_len:].lstrip(path_sep))))

offset_rewriter = partial(change_offset_rewriter, '/')


def check_instance(obj):
    if not isinstance(obj, fs.fsBase):
        raise TypeError("'%s' is not a fs.fsBase deriviative" % obj)
    return obj.location, obj


class contentsSet(object):
    """set of :class:`pkgcore.fs.fs.fsBase` objects"""

    __metaclass__ = generic_equality
    __attr_comparison__ = ('_dict',)
    __dict_kls__ = dict


    def __init__(self, initial=None, mutable=True):

        """
        :param initial: initial fs objs for this set
        :type initial: sequence
        :param mutable: controls if it modifiable after initialization
        """
        self._dict = self.__dict_kls__()
        if initial is not None:
            self._dict.update(check_instance(x) for x in initial)
        self.mutable = mutable

    def __str__(self):
        return "%s([%s])" % (self.__class__.__name__,
            ', '.join(str(x) for x in self))

    def __repr__(self):
        # this should include the id among other things
        return "%s([%s])" % (self.__class__.__name__,
            ', '.join(repr(x) for x in self))

    def add(self, obj):

        """
        add a new fs obj to the set

        :param obj: must be a derivative of :obj:`pkgcore.fs.fs.fsBase`
        """

        if not self.mutable:
            # weird, but keeping with set.
            raise AttributeError(
                "%s is frozen; no add functionality" % self.__class__)
        if not fs.isfs_obj(obj):
            raise TypeError("'%s' is not a fs.fsBase class" % str(obj))
        self._dict[obj.location] = obj

    def __delitem__(self, obj):

        """
        remove a fs obj to the set

        :type obj: a derivative of :obj:`pkgcore.fs.fs.fsBase`
            or a string location of an obj in the set.
        :raise KeyError: if the obj isn't found
        """

        if not self.mutable:
            # weird, but keeping with set.
            raise AttributeError(
                "%s is frozen; no remove functionality" % self.__class__)
        if fs.isfs_obj(obj):
            del self._dict[obj.location]
        else:
            del self._dict[normpath(obj)]

    def remove(self, obj):
        del self[obj]

    def discard(self, obj):
        if fs.isfs_obj(obj):
            self._dict.pop(obj.location, None)
        else:
            self._dict.pop(obj, None)

    def __getitem__(self, obj):
        if fs.isfs_obj(obj):
            return self._dict[obj.location]
        return self._dict[normpath(obj)]

    def __contains__(self, key):
        if fs.isfs_obj(key):
            return key.location in self._dict
        return normpath(key) in self._dict

    def clear(self):
        """
        clear the set
        :raise ttributeError: if the instance is frozen
        """
        if not self.mutable:
            # weird, but keeping with set.
            raise AttributeError(
                "%s is frozen; no clear functionality" % self.__class__)
        self._dict.clear()

    @staticmethod
    def _convert_loc(iterable):
        f = fs.isfs_obj
        for x in iterable:
            if f(x):
                yield x.location
            else:
                yield x

    @staticmethod
    def _ensure_fsbase(iterable):
        f = fs.isfs_obj
        for x in iterable:
            if not f(x):
                raise ValueError("must be an fsBase derivative: got %r" % x)
            yield x

    def difference(self, other):
        if not hasattr(other, '__contains__'):
            other = set(self._convert_loc(other))
        return contentsSet((x for x in self if x.location not in other),
            mutable=self.mutable)

    def difference_update(self, other):
        if not self.mutable:
            raise TypeError("%r isn't mutable" % self)

        rem = self.remove
        for x in other:
            if x in self:
                rem(x)

    def intersection(self, other):
        return contentsSet((x for x in other if x in self),
            mutable=self.mutable)

    def intersection_update(self, other):
        if not self.mutable:
            raise TypeError("%r isn't mutable" % self)
        if not hasattr(other, '__contains__'):
            other = set(self._convert_loc(other))

        l = [x for x in self if x.location not in other]
        for x in l:
            self.remove(x)

    def issubset(self, other):
        if not hasattr(other, '__contains__'):
            other = set(self._convert_loc(other))
        return all(x in other for x in self._dict)

    def issuperset(self, other):
        if not hasattr(other, '__contains__'):
            other = set(self._convert_loc(other))
        return all(x in self for x in other)

    def isdisjoint(self, other):
        if not hasattr(other, '__contains__'):
            other = set(self._convert_loc(other))
        return not any(x in other for x in self._dict)

    def union(self, other):
        c = contentsSet(other)
        c.update(self)
        return c

    def __iter__(self):
        return self._dict.itervalues()

    def __len__(self):
        return len(self._dict)

    def symmetric_difference(self, other):
        c = contentsSet(mutable=True)
        c.update(self)
        c.symmetric_difference_update(other)
        object.__setattr__(c, 'mutable', self.mutable)
        return c

    def symmetric_difference_update(self, other):
        if not self.mutable:
            raise TypeError("%r isn't mutable" % self)
        if not hasattr(other, '__contains__'):
            other = contentsSet(self._ensure_fsbase(other))
        l = []
        for x in self:
            if x in other:
                l.append(x)
        add = self.add
        for x in other:
            if x not in self:
                add(x)
        rem = self.remove
        for x in l:
            rem(x)
        del l, rem

    def update(self, iterable):
        d = self._dict
        for x in iterable:
            d[x.location] = x

    def iterfiles(self, invert=False):
        """A generator yielding just :obj:`pkgcore.fs.fs.fsFile` instances.

        :param invert: if True, yield everything that isn't a fsFile instance,
            else yields just fsFile instances.
        """

        if invert:
            return (x for x in self if not x.is_reg)
        return ifilter(attrgetter('is_reg'), self)

    def files(self, invert=False):
        """Returns a list of just :obj:`pkgcore.fs.fs.fsFile` instances.

        :param invert: if True, yield everything that isn't a
            fsFile instance, else yields just fsFile.
        """
        return list(self.iterfiles(invert=invert))

    def iterdirs(self, invert=False):
        if invert:
            return (x for x in self if not x.is_dir)
        return ifilter(attrgetter('is_dir'), self)

    def dirs(self, invert=False):
        return list(self.iterdirs(invert=invert))

    def itersymlinks(self, invert=False):
        if invert:
            return (x for x in self if not x.is_sym)
        return ifilter(attrgetter('is_sym'), self)

    def symlinks(self, invert=False):
        return list(self.iterlinks(invert=invert))

    iterlinks = alias_method('itersymlinks')
    links = alias_method('symlinks')

    def iterdevs(self, invert=False):
        if invert:
            return (x for x in self if not x.is_dev)
        return ifilter(attrgetter('is_dev'), self)

    def devs(self, invert=False):
        return list(self.iterdevs(invert=invert))

    def iterfifos(self, invert=False):
        if invert:
            return (x for x in self if not x.is_fifo)
        return ifilter(attrgetter('is_fifo'), self)

    def fifos(self, invert=False):
        return list(self.iterfifos(invert=invert))

    for k in ("file", "dir", "symlink", "dev", "fifo"):
        locals()['iter%ss' % k].__doc__ = \
            iterfiles.__doc__.replace('fsFile', 'fs%s' % k.capitalize())
        locals()['%ss' % k].__doc__ = \
            files.__doc__.replace('fsFile', 'fs%s' % k.capitalize())
    del k

    def inode_map(self):
        d = defaultdict(list)
        for obj in self.iterfiles():
            key = (obj.dev, obj.inode)
            if None in key:
                continue
            d[key].append(obj)
        return d

    def clone(self, empty=False):
        if empty:
            return self.__class__([], mutable=True)
        return self.__class__(self._dict.itervalues(), mutable=True)

    def insert_offset(self, offset):
        cset = self.clone(empty=True)
        cset.update(offset_rewriter(offset, self))
        return cset

    def change_offset(self, old_offset, new_offset):
        cset = self.clone(empty=True)
        cset.update(change_offset_rewriter(old_offset, new_offset, self))
        return cset

    def iter_child_nodes(self, start_point):
        """Yield a stream of nodes that are fs entries contained within the
        passed in start point.

        :param start_point: fs filepath all yielded nodes must be within.
        """

        if isinstance(start_point, fs.fsBase):
            if start_point.is_sym:
                start_point = start_point.target
            else:
                start_point = start_point.location
        for x in self:
            cn_path = normpath(start_point).rstrip(path.sep) + path.sep
            # what about sym targets?
            if x.location.startswith(cn_path):
                yield x

    def child_nodes(self, start_point):
        """Return a clone of this instance, w/ just the child nodes returned
        from `iter_child_nodes`.

        :param start_point: fs filepath all yielded nodes must be within.
        """
        obj = self.clone(empty=True)
        obj.update(self.iter_child_nodes(start_point))
        return obj

    def map_directory_structure(self, other, add_conflicting_sym=True):
        """Resolve the directory structure between this instance, and another
        contentset, collapsing syms of self into directories of other.
        """
        conflicts_d = {x: x.resolved_target for x in other.iterlinks()}
        # rebuild the targets first; sorted due to the fact that we want to
        # rewrite each node (resolving down the filepath chain)
        conflicts = sorted(contentsSet(self.iterdirs()).intersection(conflicts_d))
        obj = self.clone()
        while conflicts:
            for conflict in conflicts:
                # punt the conflict first, since we don't want it getting rewritten
                obj.remove(conflict)
                subset = obj.child_nodes(conflict.location)
                obj.difference_update(subset)
                subset = subset.change_offset(conflict.location, conflict.resolved_target)
                obj.update(subset)
                if add_conflicting_sym:
                    obj.add(other[conflicts_d[conflict]])

            # rebuild the targets first; sorted due to the fact that we want to
            # rewrite each node (resolving down the filepath chain)
            conflicts = sorted(contentsSet(obj.iterdirs()).intersection(conflicts_d))
        return obj

    def add_missing_directories(self, mode=0775, uid=0, gid=0, mtime=None):
        """Ensure that a directory node exists for each path; add if missing."""
        missing = (x.dirname for x in self)
        missing = set(x for x in missing if x not in self)
        if mtime is None:
            mtime = time.time()
        # have to go recursive since many directories may be missing.
        missing_initial = list(missing)
        for x in missing_initial:
            target = path.dirname(x)
            while target not in missing and target not in self:
                missing.add(target)
                target = path.dirname(target)
        missing.discard("/")
        self.update(fs.fsDir(location=x, mode=mode, uid=uid, gid=gid, mtime=mtime)
            for x in missing)


class OrderedContentsSet(contentsSet):

    def __init__(self, initial=None, mutable=False,
                 add_missing_directories=False):
        contentsSet.__init__(self, mutable=True)
        self._dict = OrderedDict()
        if initial:
            self.update(initial)
        # some sources are a bit stupid, tarballs for example.
        # add missing directories if requested
        if add_missing_directories:
            self.add_missing_directories()
        self.mutable = mutable
