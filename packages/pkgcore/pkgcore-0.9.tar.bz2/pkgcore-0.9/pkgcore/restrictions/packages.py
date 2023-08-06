# Copyright: 2005-2012 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

"""
restriction classes designed for package level matching
"""

from snakeoil.compatibility import is_py3k, IGNORED_EXCEPTIONS
from snakeoil.demandload import demandload
from snakeoil.klass import generic_equality, static_attrgetter

from pkgcore.restrictions import restriction, boolean

demandload("pkgcore.log:logger")

# Backwards compatibility.
package_type = restriction.package_type


class native_PackageRestriction(object):
    __slots__ = ('_pull_attr_func', '_attr_split', 'restriction', 'ignore_missing',
        'negate')

    __attr_comparison__ = ("__class__", "negate", "_attr_split", "restriction")
    __metaclass__ = generic_equality

    def __init__(self, attr, childrestriction, negate=False, ignore_missing=True):
        """
        :param attr: package attribute to match against
        :param childrestriction: a :obj:`pkgcore.restrictions.values.base` instance
        to pass attr to for matching
        :param negate: should the results be negated?
        """
        if not childrestriction.type == self.subtype:
            raise TypeError("restriction must be of type %r" % (self.subtype,))
        sf = object.__setattr__
        sf(self, "negate", negate)
        self._parse_attr(attr)
        sf(self, "restriction", childrestriction)
        sf(self, "ignore_missing", ignore_missing)

    def _parse_attr(self, attr):
        object.__setattr__(self, "_pull_attr_func", static_attrgetter(attr))
        object.__setattr__(self, "_attr_split", attr.split('.'))

    def _pull_attr(self, pkg):
        try:
            return self._pull_attr_func(pkg)
        except IGNORED_EXCEPTIONS:
            raise
        except Exception as e:
            if self._handle_exception(pkg, e, self._attr_split):
                raise
            return self.__sentinel__

    def match(self, pkg):
        attr = self._pull_attr(pkg)
        if attr is self.__sentinel__:
            return self.negate
        return self.restriction.match(attr) != self.negate


class PackageRestriction_mixin(restriction.base):
    """Package data restriction."""

    __slots__ = ()

    # note __sentinel__ is used purely because the codepath that use it can
    # get executed a *lot*, and setup/tear down of exception machinery can
    # be surprisingly costly

    __sentinel__ = object()

    # Careful: some methods (__eq__, __hash__, intersect) try to work
    # for subclasses too. They will not behave as intended if a
    # subclass adds attributes. So if you do that, override the
    # methods.

    type = restriction.package_type
    subtype = restriction.value_type
    conditional = False

    def _handle_exception(self, pkg, exc, attr_split):
        if isinstance(exc, AttributeError):
            if not self.ignore_missing:
                logger.exception("failed getting attribute %s from %s, "
                              "exception %s" % ('.'.join(attr_split), str(pkg), str(exc)))

            eargs = [x for x in exc.args if isinstance(x, basestring)]
            if any(x in attr_split for x in eargs):
                return False
            elif any("'%s'" % x in y for x in attr_split for y in eargs):
                # this is fairly horrible; probably specific to cpython also.
                # either way, does a lookup specifically for attr components
                # in the string exception string, looking for 'attr' in the
                # text.
                # if it doesn't match, exception is thrown.
                return False
        logger.exception("caught unexpected exception accessing %s from %s, "
            "exception %s" % ('.'.join(attr_split), str(pkg), str(exc)))
        return True

    def force_False(self, pkg):
        attr = self._pull_attr(pkg)
        if attr is self.__sentinel__:
            return not self.negate
        if self.negate:
            return self.restriction.force_True(pkg, self.attr, attr)
        return self.restriction.force_False(pkg, self.attr, attr)

    def force_True(self, pkg):
        attr = self._pull_attr(pkg)
        if attr is self.__sentinel__:
            return self.negate
        if self.negate:
            return self.restriction.force_False(pkg, self.attr, attr)
        return self.restriction.force_True(pkg, self.attr, attr)

    def __len__(self):
        if not isinstance(self.restriction, boolean.base):
            return 1
        return len(self.restriction) + 1

    def __hash__(self):
        return hash((self.negate, self.attrs, self.restriction))

    def __str__(self):
        s = "%s " % (self.attrs, )
        if self.negate:
            s += "not "
        return s + str(self.restriction)

    def __repr__(self):
        if self.negate:
            string = '<%s attr=%r restriction=%r negated @%#8x>'
        else:
            string = '<%s attr=%r restriction=%r @%#8x>'
        return string % (
            self.__class__.__name__, self.attr, self.restriction, id(self))

    @property
    def attr(self):
        return '.'.join(self._attr_split)

    @property
    def attrs(self):
        return (self.attr,)


class native_PackageRestrictionMulti(native_PackageRestriction):

    __slots__ = ()

    @property
    def attrs(self):
        return tuple('.'.join(x) for x in self._attr_split)

    def _parse_attr(self, attrs):
        object.__setattr__(self, '_pull_attr_func',
            tuple(map(static_attrgetter, attrs)))
        object.__setattr__(self, '_attr_split', tuple(x.split('.') for x in attrs))

    def _pull_attr(self, pkg):
        val = []
        try:
            for attr_func in self._pull_attr_func:
                val.append(attr_func(pkg))
        except IGNORED_EXCEPTIONS:
            raise
        except Exception as e:
            if self._handle_exception(pkg, e,
                self._attr_split[len(val)]):
                raise
            return self.__sentinel__
        return val


class PackageRestrictionMulti_mixin(PackageRestriction_mixin):

    __slots__ = ()

    attr = None

    def force_False(self, pkg):
        attrs = self._pull_attr(pkg)
        if attrs is self.__sentinel__:
            return not self.negate
        if self.negate:
            return self.restriction.force_True(pkg, self.attrs, attrs)
        return self.restriction.force_False(pkg, self.attrs, attrs)

    def force_True(self, pkg):
        attrs = self._pull_attr(pkg)
        if attrs is self.__sentinel__:
            return self.negate
        if self.negate:
            return self.restriction.force_False(pkg, self.attrs, attrs)
        return self.restriction.force_True(pkg, self.attrs, attrs)

    @property
    def attrs(self):
        return tuple('.'.join(x) for x in self._attr_split)


try:
    from pkgcore.restrictions._restrictions import \
        PackageRestriction as PackageRestriction_base
except ImportError:
    PackageRestriction_base = native_PackageRestriction
PackageRestrictionMulti_base = native_PackageRestrictionMulti


class PackageRestriction(PackageRestriction_base, PackageRestriction_mixin):
    __slots__ = ()
    __inst_caching__ = True

    if is_py3k:
        __hash__ = PackageRestriction_mixin.__hash__
        __eq__ = PackageRestriction_base.__eq__


class PackageRestrictionMulti(PackageRestrictionMulti_base,
    PackageRestrictionMulti_mixin):

    __slots__ = ()
    __inst_caching__ = True

    if is_py3k:
        __hash__ = PackageRestriction_mixin.__hash__
        __eq__ = PackageRestriction_base.__eq__


class Conditional(PackageRestriction):

    """
    base object representing a conditional package restriction

    used to control whether a payload of restrictions are accessible or not
    """

    __slots__ = ('payload',)

    __attr_comparison__ = ("__class__", "negate", "attr", "restriction",
        "payload")
    __metaclass__ = generic_equality
    conditional = True

    # note that instance caching is turned off.
    # rarely pays off for conditionals from a speed/mem comparison

    def __init__(self, attr, childrestriction, payload, **kwds):
        """
        :param attr: attr to match against
        :param childrestriction: restriction to control whether or not the
            payload is accessible
        :param payload: payload data, whatever it may be.
        :param kwds: additional args to pass to :obj:`PackageRestriction`
        """
        PackageRestriction.__init__(self, attr, childrestriction, **kwds)
        object.__setattr__(self, "payload", tuple(payload))

    def __str__(self):
        return "( Conditional: %s payload: [ %s ] )" % (
            PackageRestriction.__str__(self),
            ", ".join(str(x) for x in self.payload))

    def __repr__(self):
        if self.negate:
            string = '<%s attr=%r restriction=%r payload=%r negated @%#8x>'
        else:
            string = '<%s attr=%r restriction=%r payload=%r @%#8x>'
        return string % (
            self.__class__.__name__, self.attr, self.restriction, self.payload,
            id(self))

    def __iter__(self):
        return iter(self.payload)

    def __hash__(self):
        return hash((self.attr, self.negate, self.restriction, self.payload))

    def evaluate_conditionals(self, parent_cls, parent_seq, enabled, tristate_locked=None):
        if tristate_locked is not None:
            assert len(self.restriction.vals) == 1
            val = list(self.restriction.vals)[0]
            if val in tristate_locked:
                # if val is forced true, but the check is
                # negation ignore it
                # if !mips != mips
                if (val in enabled) == self.restriction.negate:
                    return
        elif not self.restriction.match(enabled):
            return

        if self.payload:
            boolean.AndRestriction(*self.payload).evaluate_conditionals(parent_cls, parent_seq,
                enabled, tristate_locked)



# "Invalid name" (pylint uses the module const regexp, not the class regexp)
# pylint: disable-msg=C0103

AndRestriction = restriction.curry_node_type(boolean.AndRestriction,
                                             restriction.package_type)
OrRestriction = restriction.curry_node_type(boolean.OrRestriction,
                                            restriction.package_type)

AlwaysBool = restriction.curry_node_type(restriction.AlwaysBool,
                                         restriction.package_type)

class KeyedAndRestriction(boolean.AndRestriction):

    type = package_type

    def __init__(self, *a, **kwds):
        key = kwds.pop("key", None)
        tag = kwds.pop("tag", None)
        boolean.AndRestriction.__init__(self, *a, **kwds)
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "tag", tag)

    def __str__(self):
        if self.tag is None:
            return boolean.AndRestriction.__str__(self)
        return "%s %s" % (self.tag, boolean.AndRestriction.__str__(self))

AlwaysTrue = AlwaysBool(negate=True)
AlwaysFalse = AlwaysBool(negate=False)
