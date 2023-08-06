# Copyright: 2006 Brian Harring <ferringb@gmail.com
# Copyright: 2006 Marien Zwart <marienz@gentoo.org>
# License: BSD/GPL2

from snakeoil.currying import post_curry

from pkgcore.ebuild import restricts
from pkgcore.ebuild.atom import atom
from pkgcore.repository import util
from pkgcore.restrictions import packages, values, boolean, restriction
from pkgcore.test import TestCase
from pkgcore.util import parserestrict


class MatchTest(TestCase):

    def test_comma_separated_containment(self):
        parser = parserestrict.comma_separated_containment('utensil')
        restrict = parser('spork,foon')
        # Icky, should really try to match a fake package.
        self.assertInstance(restrict, packages.PackageRestriction)
        self.assertEqual('utensil', restrict.attr)
        valrestrict = restrict.restriction
        self.assertTrue(valrestrict.match(('foon',)))
        self.assertFalse(valrestrict.match(('spork,foon',)))
        self.assertFalse(valrestrict.match(('foo',)))


class TestExtendedRestrictionGeneration(TestCase):

    def assertInstance(self, restrict, kls, token):
        TestCase.assertInstance(
            self, restrict, kls,
            msg="got %r, expected %r for %r" % (restrict, kls, token))

    def verify_text_glob(self, restrict, token):
        self.assertInstance(restrict, values.StrRegex, token)

    def verify_text(self, restrict, token):
        self.assertInstance(restrict, values.StrExactMatch, token)
        self.assertEqual(restrict.exact, token)

    def test_convert_glob(self):
        self.verify_text(parserestrict.convert_glob("diffball"), "diffball")
        for token in ("diff*", "*diff"):
            self.verify_text_glob(parserestrict.convert_glob(token), token)

        for token in ("*", ""):
            i = parserestrict.convert_glob(token)
            self.assertEqual(
                i, None,
                msg="verifying None is returned on pointless restrictions,"
                    " failed token: %r" % (token,))

        self.assertRaises(
            parserestrict.ParseError, parserestrict.convert_glob, '**')

    def verify_restrict(self, restrict, attr, token):
        self.assertInstance(restrict, packages.PackageRestriction, token)
        self.assertEqual(
            restrict.attr, attr,
            msg="verifying package attr %r; required(%s), token %s" % (
                restrict.attr, attr, token))

        if "*" in token:
            self.verify_text_glob(restrict.restriction, token)
        else:
            self.verify_text(restrict.restriction, token)

    def generic_single_restrict_check(self, iscat):
        if iscat:
            sfmts = ["%s/*"]
            attr = "category"
        else:
            sfmts = ["*/%s", "%s"]
            attr = "package"

        for sfmt in sfmts:
            for raw_token in ("package", "*bsdiff", "bsdiff*"):
                token = sfmt % raw_token
                i = parserestrict.parse_match(token)
                self.verify_restrict(i, attr, raw_token)

    test_category = post_curry(generic_single_restrict_check, True)
    test_package = post_curry(generic_single_restrict_check, False)

    def test_combined(self):
        self.assertInstance(
            parserestrict.parse_match("dev-util/diffball"),
            atom, "dev-util/diffball")
        for token in ("dev-*/util", "dev-*/util*", "dev-a/util*"):
            i = parserestrict.parse_match(token)
            self.assertInstance(i, boolean.AndRestriction, token)
            self.assertEqual(len(i), 2)
            self.verify_restrict(i[0], "category", token.split("/")[0])
            self.verify_restrict(i[1], "package", token.split("/")[1])

    def test_globs(self):
        for token in ("*", "*/*"):
            i = parserestrict.parse_match(token)
            self.assertInstance(i, restriction.AlwaysBool, token)
            self.assertEqual(len(i), 1)

        for token in ("*::gentoo", "*/*::gentoo"):
            i = parserestrict.parse_match(token)
            self.assertInstance(i, boolean.AndRestriction, token)
            self.assertEqual(len(i), 2)
            self.assertInstance(i[0], restricts.RepositoryDep, token.split("::")[1])
            self.assertInstance(i[1], restriction.AlwaysBool, token.split("::")[0])

        for token in ("foo*::gentoo", "*foo::gentoo"):
            i = parserestrict.parse_match(token)
            self.assertInstance(i, boolean.AndRestriction, token)
            self.assertEqual(len(i), 2)
            self.assertInstance(i[0], restricts.RepositoryDep, token.split("::")[1])
            self.verify_restrict(i[1], "package", token.split("::")[0])

        for token, attr, n in (
                ("foo/*::gentoo", "category", 0),
                ("*/foo::gentoo", "package", 1),
                ):
            i = parserestrict.parse_match(token)
            self.assertInstance(i, boolean.AndRestriction, token)
            self.assertEqual(len(i), 2)
            self.assertInstance(i[0], restricts.RepositoryDep, token.split("::")[1])
            self.verify_restrict(i[1], attr, token.split("::")[0].split("/")[n])

    def test_atom_globbed(self):
        self.assertInstance(
            parserestrict.parse_match("=sys-devel/gcc-4*"),
            atom, "=sys-devel/gcc-4*")

    def test_use_atom(self):
        o = parserestrict.parse_match("net-misc/openssh[-X]")
        self.assertInstance(o, atom, "net-misc/openssh[-X]")
        self.assertTrue(o.use)

    def test_slot_atom(self):
        o = parserestrict.parse_match("sys-devel/automake:1.6")
        self.assertInstance(o, atom, "sys-devel/automake:1.6")
        self.assertTrue(o.slot)

    def test_subslot_atom(self):
        o = parserestrict.parse_match("dev-libs/boost:0/1.54")
        self.assertInstance(o, atom, "dev-libs/boost:0/1.54")
        self.assertTrue(o.slot)
        self.assertTrue(o.subslot)

    def test_exceptions(self):
        pm = parserestrict.parse_match
        pe = parserestrict.ParseError
        for token in (
                "!dev-util/diffball",
                "dev-util/diffball-0.4",
                "=dev-util/*diffball-0.4",
                "=*/diffball-0.4",
                "::gentoo",
                ):
            self.assertRaises(pe, pm, token)


class ParsePVTest(TestCase):

    def setUp(self):
        self.repo = util.SimpleTree({
            'spork': {
                'foon': ('1', '2'),
                'spork': ('1', '2'),
                },
            'foon': {
                'foon': ('2', '3'),
                }})

    def test_parse_pv(self):
        for input, output in (
                ('spork/foon-3', 'spork/foon-3'),
                ('spork-1', 'spork/spork-1'),
                ('foon-3', 'foon/foon-3'),
                ):
            self.assertEqual(
                output,
                parserestrict.parse_pv(self.repo, input).cpvstr)
        for bogus in (
                'spork',
                'foon-2',
                ):
            self.assertRaises(
                parserestrict.ParseError,
                parserestrict.parse_pv, self.repo, bogus)
