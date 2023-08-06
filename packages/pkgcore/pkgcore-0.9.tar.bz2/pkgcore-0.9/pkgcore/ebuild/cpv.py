# Copyright: 2005-2011 Brian Harring <ferringb@gmail.com>
# Copyright: 2005 Jason Stubbs <jstubbs@gentoo.org>
# License: GPL2/BSD


"""gentoo ebuild specific base package class"""

__all__ = ("CPV", "versioned_CPV", "unversioned_CPV")

from itertools import izip

from snakeoil.compatibility import cmp
from snakeoil.demandload import demandload, demand_compile_regexp
from snakeoil.klass import inject_richcmp_methods_from_cmp

from pkgcore.ebuild.errors import InvalidCPV
from pkgcore.package import base

# do this to break the cycle.
demandload("pkgcore.ebuild:atom")

demand_compile_regexp(
    'suffix_regexp', '^(alpha|beta|rc|pre|p)(\\d*)$')

suffix_value = {"pre": -2, "p": 1, "alpha": -4, "beta": -3, "rc": -1}

# while the package section looks fugly, there is a reason for it-
# to prevent version chunks from showing up in the package

demand_compile_regexp(
    'isvalid_version_re',
    r"^(?:\d+)(?:\.\d+)*[a-zA-Z]?(?:_(p(?:re)?|beta|alpha|rc)\d*)*$")

demand_compile_regexp(
    'isvalid_cat_re', r"^(?:[a-zA-Z0-9][-a-zA-Z0-9+._]*(?:/(?!$))?)+$")

# empty string is fine, means a -- was encounter.
demand_compile_regexp(
    '_pkg_re', r"^[a-zA-Z0-9+_]+$")


def isvalid_pkg_name(chunks):
    if not chunks[0] or chunks[0][0] == '+':
        # this means a leading -; additionally, '+asdf' is disallowed
        return False
    mf = _pkg_re.match
    if not all(mf(s) for s in chunks[:-1]):
        return False
    if chunks[-1]:
        return mf(chunks[-1]) and not isvalid_version_re.match(chunks[-1])
    return True

def isvalid_rev(s):
    return s and s[0] == 'r' and s[1:].isdigit()


class _native_CPV(object):

    """
    base ebuild package class

    :ivar category: str category
    :ivar package: str package
    :ivar key: strkey (cat/pkg)
    :ivar version: str version
    :ivar revision: int revision
    :ivar versioned_atom: atom matching this exact version
    :ivar unversioned_atom: atom matching all versions of this package
    :cvar _get_attr: mapping of attr:callable to generate attributes on the fly
    """

    __slots__ = ("__weakref__", "cpvstr", "key", "category", "package",
        "version", "revision", "fullver")

    # if native is being used, forget trying to reuse strings.
    def __init__(self, *a, **kwds):
        """
        Can be called with one string or with three string args.

        If called with one arg that is the cpv string. (See :obj:`parser`
        for allowed syntax).

        If called with three args they are the category, package and
        version components of the cpv string respectively.
        """
        versioned = True
        had_versioned = 'versioned' in kwds
        if had_versioned:
            versioned = kwds.pop("versioned")
        if kwds:
            raise TypeError("versioned is the only allowed kwds: %r" % (kwds,))
        l = len(a)
        if l == 1:
            cpvstr = a[0]
            if not had_versioned:
                raise TypeError("single arguement invocation requires versioned kwd; %r"
                    % (cpvstr,))
        elif l == 3:
            for x in a:
                if not isinstance(x, basestring):
                    raise TypeError("all args must be strings, got %r" % (a,))
            cpvstr = "%s/%s-%s" % a
            versioned = True
        else:
            raise TypeError("CPV takes 1 arg (cpvstr), or 3 (cat, pkg, ver):"
                " got %r" % (a,))
        if not isinstance(cpvstr, basestring):
            raise TypeError(self.cpvstr)

        try:
            categories, pkgver  = cpvstr.rsplit("/", 1)
        except ValueError:
            # occurs if the rsplit yields only one item
            raise InvalidCPV(cpvstr)
        if not isvalid_cat_re.match(categories):
            raise InvalidCPV(cpvstr)
        sf = object.__setattr__
        sf(self, 'category', categories)
        sf(self, 'cpvstr', cpvstr)
        pkg_chunks = pkgver.split("-")
        lpkg_chunks = len(pkg_chunks)
        if versioned:
            if lpkg_chunks == 1:
                raise InvalidCPV(cpvstr)
            if isvalid_rev(pkg_chunks[-1]):
                if lpkg_chunks < 3:
                    # needs at least ('pkg', 'ver', 'rev')
                    raise InvalidCPV(cpvstr)
                rev = int(pkg_chunks.pop(-1)[1:])
                if not rev:
                    rev = None
                    # reset the stored cpvstr to drop -r0+
                    sf(self, 'cpvstr', "%s/%s" % (categories,
                        '-'.join(pkg_chunks)))
                sf(self, 'revision', rev)
            else:
                sf(self, 'revision', None)

            if not isvalid_version_re.match(pkg_chunks[-1]):
                raise InvalidCPV(cpvstr)
            sf(self, 'version', pkg_chunks.pop(-1))
            if self.revision:
                sf(self, 'fullver', "%s-r%s" % (self.version, self.revision))
            else:
                sf(self, 'fullver', self.version)

            if not isvalid_pkg_name(pkg_chunks):
                raise InvalidCPV(cpvstr)
            sf(self, 'package', '-'.join(pkg_chunks))
            sf(self, 'key', "%s/%s" % (categories, self.package))
        else:
            if not isvalid_pkg_name(pkg_chunks):
                raise InvalidCPV(cpvstr)
            sf(self, 'revision', None)
            sf(self, 'fullver', None)
            sf(self, 'version', None)
            sf(self, 'key', cpvstr)
            sf(self, 'package', '-'.join(pkg_chunks))

    def __hash__(self):
        return hash(self.cpvstr)

    def __repr__(self):
        return '<%s cpvstr=%s @%#8x>' % (
             self.__class__.__name__, getattr(self, 'cpvstr', None), id(self))

    def __str__(self):
        return getattr(self, 'cpvstr', 'None')

    def __cmp__(self, other):
        try:
            if self.cpvstr == other.cpvstr:
                return 0

            if (self.category and other.category and self.category != other.category):
                return cmp(self.category, other.category)

            if self.package and other.package and self.package != other.package:
                return cmp(self.package, other.package)

            # note I chucked out valueerror, none checks on versions
            # passed in. I suck, I know.
            # ~harring
            # fails in doing comparison of unversioned atoms against
            # versioned atoms
            return native_ver_cmp(self.version, self.revision, other.version,
                              other.revision)
        except AttributeError:
            return 1


def native_ver_cmp(ver1, rev1, ver2, rev2):

    # If the versions are the same, comparing revisions will suffice.
    if ver1 == ver2:
        return cmp(rev1, rev2)

    # Split up the versions into dotted strings and lists of suffixes.
    parts1 = ver1.split("_")
    parts2 = ver2.split("_")

    # If the dotted strings are equal, we can skip doing a detailed comparison.
    if parts1[0] != parts2[0]:

        # First split up the dotted strings into their components.
        ver_parts1 = parts1[0].split(".")
        ver_parts2 = parts2[0].split(".")

        # Pull out any letter suffix on the final components and keep
        # them for later.
        letters = []
        for ver_parts in (ver_parts1, ver_parts2):
            if ver_parts[-1][-1].isalpha():
                letters.append(ord(ver_parts[-1][-1]))
                ver_parts[-1] = ver_parts[-1][:-1]
            else:
                # Using -1 simplifies comparisons later
                letters.append(-1)

        # OPT: Pull length calculation out of the loop
        ver_parts1_len = len(ver_parts1)
        ver_parts2_len = len(ver_parts2)

        # Iterate through the components
        for v1, v2 in izip(ver_parts1, ver_parts2):

            # If the string components are equal, the numerical
            # components will be equal too.
            if v1 == v2:
                continue

            # If one of the components begins with a "0" then they
            # are compared as floats so that 1.1 > 1.02; else ints.
            if v1[0] != "0" and v2[0] != "0":
                v1 = int(v1)
                v2 = int(v2)
            else:
                # handle the 0.060 == 0.060 case.
                v1 = v1.rstrip("0")
                v2 = v2.rstrip("0")

            # If they are not equal, the higher value wins.
            c = cmp(v1, v2)
            if c:
                return c

        if ver_parts1_len > ver_parts2_len:
            return 1
        elif ver_parts2_len > ver_parts1_len:
            return -1

        # The dotted components were equal. Let's compare any single
        # letter suffixes.
        if letters[0] != letters[1]:
            return cmp(letters[0], letters[1])

    # The dotted components were equal, so remove them from our lists
    # leaving only suffixes.
    del parts1[0]
    del parts2[0]

    # OPT: Pull length calculation out of the loop
    parts1_len = len(parts1)
    parts2_len = len(parts2)

    # Iterate through the suffixes
    for x in xrange(max(parts1_len, parts2_len)):

        # If we're at the end of one of our lists, we need to use
        # the next suffix from the other list to decide who wins.
        if x == parts1_len:
            match = suffix_regexp.match(parts2[x])
            val = suffix_value[match.group(1)]
            if val:
                return cmp(0, val)
            return cmp(0, int("0"+match.group(2)))
        if x == parts2_len:
            match = suffix_regexp.match(parts1[x])
            val = suffix_value[match.group(1)]
            if val:
                return cmp(val, 0)
            return cmp(int("0"+match.group(2)), 0)

        # If the string values are equal, no need to parse them.
        # Continue on to the next.
        if parts1[x] == parts2[x]:
            continue

        # Match against our regular expression to make a split between
        # "beta" and "1" in "beta1"
        match1 = suffix_regexp.match(parts1[x])
        match2 = suffix_regexp.match(parts2[x])

        # If our int'ified suffix names are different, use that as the basis
        # for comparison.
        c = cmp(suffix_value[match1.group(1)], suffix_value[match2.group(1)])
        if c:
            return c

        # Otherwise use the digit as the basis for comparison.
        c = cmp(int("0"+match1.group(2)), int("0"+match2.group(2)))
        if c:
            return c

    # Our versions had different strings but ended up being equal.
    # The revision holds the final difference.
    return cmp(rev1, rev2)

fake_cat = "fake"
fake_pkg = "pkg"
def cpy_ver_cmp(ver1, rev1, ver2, rev2):
    if ver1 == ver2:
        return cmp(rev1, rev2)
    if ver1 is None:
        ver1 = ''
    if ver2 is None:
        ver2 = ''
    c = cmp(cpy_CPV(fake_cat, fake_pkg, ver1, versioned=bool(ver1)),
            cpy_CPV(fake_cat, fake_pkg, ver2, versioned=bool(ver2)))
    if c != 0:
        return c
    return cmp(rev1, rev2)


def mk_cpv_cls(base_cls):
    class CPV(base.base, base_cls):

        """
        base ebuild package class

        :ivar category: str category
        :ivar package: str package
        :ivar key: strkey (cat/pkg)
        :ivar version: str version
        :ivar revision: int revision
        :ivar versioned_atom: atom matching this exact version
        :ivar unversioned_atom: atom matching all versions of this package
        :cvar _get_attr: mapping of attr:callable to generate attributes on the fly
        """

        __slots__ = ()

        inject_richcmp_methods_from_cmp(locals())
#       __metaclass__ = WeakInstMeta

#       __inst_caching__ = True

        def __repr__(self):
            return '<%s cpvstr=%s @%#8x>' % (
                self.__class__.__name__, getattr(self, 'cpvstr', None),
                id(self))

        # for some insane reason, py3k doesn't pick up the __hash__... add it
        # manually.
        __hash__ = base_cls.__hash__

        @property
        def versioned_atom(self):
            return atom.atom("=%s" % self.cpvstr)

        @property
        def unversioned_atom(self):
            return atom.atom(self.key)

        @classmethod
        def versioned(cls, *args):
            return cls(versioned=True, *args)

        @classmethod
        def unversioned(cls, *args):
            return cls(versioned=False, *args)

        def __reduce__(self):
            return (self.__class__, (self.cpvstr,), None, None, None)

    return CPV

native_CPV = mk_cpv_cls(_native_CPV)

try:
    # No name in module
    # pylint: disable-msg=E0611
    from pkgcore.ebuild._cpv import CPV as cpy_CPV
    CPV_base = cpy_CPV
    ver_cmp = cpy_ver_cmp
    cpy_builtin = True
    cpy_CPV = CPV = mk_cpv_cls(cpy_CPV)
except ImportError:
    ver_cmp = native_ver_cmp
    cpy_builtin = False
    CPV = CPV_base = native_CPV

def unversioned_CPV(*args):
    return CPV.unversioned(*args)

def versioned_CPV(*args):
    return CPV.versioned(*args)

versioned_CPV = CPV.versioned
unversioned_CPV = CPV.unversioned

class versioned_CPV_cls(CPV):

    __slots__ = ()

    def __init__(self, *args):
        CPV.__init__(self, versioned=True, *args)
