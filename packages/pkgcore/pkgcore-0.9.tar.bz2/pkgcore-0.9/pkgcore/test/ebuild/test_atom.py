# Copyright: 2006-2011 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

from functools import partial

from snakeoil.compatibility import cmp
from snakeoil.pickling import dumps, loads
from snakeoil.test import mk_cpy_loadable_testcase

from pkgcore import test
from pkgcore.ebuild import atom, errors, restricts
from pkgcore.ebuild.cpv import CPV
from pkgcore.restrictions.boolean import AndRestriction
from pkgcore.test.misc import FakePkg, FakeRepo


class Test_native_atom(test.TestRestriction):

    class kls(atom.atom):
        locals().update(atom.native_atom_overrides.iteritems())
        __inst_caching__ = True
        __slots__ = ()

    kls = staticmethod(kls)

    def test_removed_features(self):
        # Ensure multi-slots no longer are allowed.
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/diffball:1,2")
        self.assertEqual(self.kls("dev-util/diffball:1").slot, "1")

    def test_solutions(self):
        d = self.kls("=dev-util/diffball-0.7.1:2")
        self.assertEqual(list(d.iter_dnf_solutions()), [[d]])
        self.assertEqual(d.dnf_solutions(), [[d]])
        self.assertEqual(list(d.iter_cnf_solutions()), [[d]])
        self.assertEqual(d.cnf_solutions(), [[d]])
        bd = AndRestriction(*d.restrictions)
        self.assertEqual(list(d.iter_dnf_solutions(True)), bd.dnf_solutions())
        self.assertEqual(list(d.iter_cnf_solutions(True)), bd.cnf_solutions())
        self.assertEqual(d.dnf_solutions(True), bd.dnf_solutions())
        self.assertEqual(d.cnf_solutions(True), bd.cnf_solutions())

    def test_str_hash(self):
        for s in ("dev-util/diffball", "=dev-util/diffball-0.7.1",
            ">foon/bar-1:2[-4,3]", "=foon/bar-2*", "~foon/bar-2.3",
            "!dev-util/diffball", "!=dev-util/diffball-0.7*",
            "foon/bar::gentoo", ">=foon/bar-10_alpha1:1::gentoo[-not,use]",
            "!!dev-util/diffball[use]"):
            self.assertEqual(str(self.kls(s)), s)
            self.assertEqual(hash(self.kls(s, disable_inst_caching=True)),
                hash(self.kls(s, disable_inst_caching=True)))

    def test_blockers(self):
        self.assertRaises(errors.MalformedAtom, self.kls,
            "!!dev-util/diffball", eapi=0)
        self.assertRaises(errors.MalformedAtom, self.kls,
            "!!dev-util/diffball", eapi=1)
        self.assertRaises(errors.MalformedAtom, self.kls,
            "!!!dev-util/diffball", eapi=2)
        for x in xrange(0,2):
            obj = self.kls("!dev-util/diffball", eapi=x)
            self.assertTrue(obj.blocks)
            self.assertTrue(obj.blocks_temp_ignorable)
            self.assertFalse(obj.blocks_strongly)
        obj = self.kls("!!dev-util/diffball", eapi=2)
        self.assertTrue(obj.blocks)
        self.assertFalse(obj.blocks_temp_ignorable)
        self.assertTrue(obj.blocks_strongly)


    def test_iter(self):
        d = self.kls("!>=dev-util/diffball-0.7:1::gentoo[use,x]")
        self.assertEqual(list(d), list(d.restrictions))

    def test_pickling(self):
        a = self.kls("dev-util/diffball")
        self.assertEqual(a, loads(dumps(a)))
        a = self.kls("dev-util/diffball", negate_vers=True)
        self.assertEqual(a, loads(dumps(a)))

    def test_glob(self):
        self.assertRaises(errors.MalformedAtom, self.kls,
            "dev-util/diffball-1*")
        self.assertRaises(errors.MalformedAtom, self.kls,
            "dev-util/diffball-1.*")

        a = self.kls("=dev-util/diffball-1.2*")
        self.assertMatch(a, FakePkg("dev-util/diffball-1.2"))
        self.assertMatch(a, FakePkg("dev-util/diffball-1.2.0"))
        self.assertMatch(a, FakePkg("dev-util/diffball-1.2-r1"))
        self.assertMatch(a, FakePkg("dev-util/diffball-1.2_alpha"))
        self.assertNotMatch(a, FakePkg("dev-util/diffball-1"))

    def test_nonversioned(self):
        a = self.kls("kde-base/kde")
        self.assertMatch(a, CPV.unversioned("kde-base/kde"))
        self.assertNotMatch(a, CPV.unversioned("kde-base/kde2"))
        self.assertMatch(a, CPV.versioned("kde-base/kde-3"))

    def make_atom(self, s, ops, ver):
        l = []
        if -1 in ops:
            l.append(">")
        if 0 in ops:
            l.append("=")
        if 1 in ops:
            l.append("<")
        return self.kls("%s%s-%s" % (''.join(l), s, ver))

    def test_versioned(self):
        astr = "app-arch/tarsync"
        le_cpv = CPV.versioned("%s-0" % astr)
        eq_cpv = CPV.versioned("%s-1.1-r2" % astr)
        ge_cpv = CPV.versioned("%s-2" % astr)
        # <, =, >
        ops = (-1, 0, 1)

        for ops, ver in ((-1, "1.0"), (-1, "1.1"),
            (0, "1.1-r2"), (1, "1.1-r3"), (1, "1.2")):
            if not isinstance(ops, (list, tuple)):
                ops = (ops,)
            a = self.make_atom(astr, ops, ver)
            if -1 in ops:
                self.assertMatch(a, ge_cpv)
                self.assertMatch(a, eq_cpv)
                self.assertNotMatch(a, le_cpv)
            if 0 in ops:
                self.assertTrue(a.match(eq_cpv))
                if ops == (0,):
                    self.assertNotMatch(a, le_cpv)
                    self.assertNotMatch(a, ge_cpv)
            if 1 in ops:
                self.assertNotMatch(a, ge_cpv)
                self.assertMatch(a, eq_cpv)
                self.assertMatch(a, le_cpv)

    def test_norev(self):
        astr = "app-arch/tarsync"
        a = self.kls("~%s-1" % astr)
        self.assertMatch(a, CPV.versioned("%s-1" % astr))
        self.assertMatch(a, CPV.versioned("%s-1-r1" % astr))
        self.assertMatch(a, CPV.versioned("%s-1-r0" % astr))
        self.assertNotMatch(a, CPV.versioned("%s-2" % astr))
        self.assertRaises(errors.MalformedAtom, self.kls, "~%s-r1" % astr)
        self.assertRaises(errors.MalformedAtom, self.kls, "~%s-r2" % astr)
        # special case- yes -r0 effectively is None, but -r shouldn't be used
        # with ~
        self.assertRaises(errors.MalformedAtom, self.kls, "~%s-r0" % astr)

    def check_use(self, eapi, defaults=False):
        astr = "dev-util/bsdiff"
        c = FakePkg("%s-1" % astr, use=("debug",), iuse=("debug", "foon"), slot=1)

        kls = partial(self.kls, eapi=eapi)

        # Valid chars: [a-zA-Z0-9_@+-]
        kls('%s[zZaA09]' % astr)
        kls('%s[x@y]' % astr)
        kls('%s[x+y]' % astr)
        kls('%s[x-y]' % astr)
        kls('%s[x_y]' % astr)
        kls('%s[-x_y]' % astr)
        kls('%s[x?]' % astr)
        kls('%s[!x?]' % astr)
        kls('%s[x=]' % astr)
        kls('%s[!x=]' % astr)

        if defaults:
            kls('%s[x(+)]' % astr)
            kls('%s[x(-)]' % astr)
            self.assertRaises(errors.MalformedAtom, kls, '%s[x(+-)]' % astr)
            self.assertRaises(errors.MalformedAtom, kls, '%s[x(@)]' % astr)
            self.assertMatch(kls("%s[debug(+)]" % astr), c)
            self.assertMatch(kls("%s[debug(-)]" % astr), c)
            self.assertMatch(kls("%s[missing(+)]" % astr), c)
            self.assertNotMatch(kls("%s[missing(-)]" % astr), c)
            self.assertMatch(kls("%s[missing(+)]" % astr), c)
            self.assertMatch(kls("%s[-missing(-)]" % astr), c)
            self.assertNotMatch(kls("%s[-missing(+)]" % astr), c)

            self.assertMatch(kls("%s[-missing(-),debug]" % astr), c)
            self.assertNotMatch(kls("%s[-missing(+),debug(+)]" % astr), c)
            self.assertMatch(kls("%s[missing(+),debug(+)]" % astr), c)
        else:
            self.assertRaises(errors.MalformedAtom, kls, '%s[x(+)]' % astr)
            self.assertRaises(errors.MalformedAtom, kls, '%s[x(-)]' % astr)

        # '.' not a valid char in use deps
        self.assertRaises(errors.MalformedAtom, kls, "%s[x.y]" % astr)

        # Use deps start with an alphanumeric char (non-transitive)
        self.assertRaises(errors.MalformedAtom, kls, "%s[@x]" % astr)
        self.assertRaises(errors.MalformedAtom, kls, "%s[_x]" % astr)
        self.assertRaises(errors.MalformedAtom, kls, "%s[+x]" % astr)
        self.assertRaises(errors.MalformedAtom, kls, "%s[-@x]" % astr)
        self.assertRaises(errors.MalformedAtom, kls, "%s[-_x]" % astr)
        self.assertRaises(errors.MalformedAtom, kls, "%s[-+x]" % astr)
        self.assertRaises(errors.MalformedAtom, kls, "%s[--x]" % astr)

        self.assertMatch(kls("%s[debug]" % astr), c)
        self.assertNotMatch(kls("%s[-debug]" % astr), c)
        self.assertMatch(kls("%s[debug,-not]" % astr), c)
        self.assertMatch(kls("%s:1[debug,-not]" % astr), c)

        self.assertRaises(errors.MalformedAtom, kls, "%s[]" % astr)
        self.assertRaises(errors.MalformedAtom, kls, "%s[-]" % astr)
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[foon")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[[fo]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[x][y]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[x]:1")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[x]a")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[--]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[x??]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[x=?]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[x?=]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[x==]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[x??]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[!=]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[!?]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[!!x?]")
        self.assertRaises(errors.MalformedAtom, kls, "dev-util/diffball[!-x?]")

    def test_slot(self):
        astr = "dev-util/confcache"
        c = FakePkg("%s-1" % astr, slot=1)
        self.assertNotMatch(self.kls("%s:0" % astr), c)
        self.assertMatch(self.kls("%s:1" % astr), c)
        self.assertNotMatch(self.kls("%s:2" % astr), c)
        # note the above isn't compliant with eapi2/3; thus this test
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foo:0", eapi=0)

        # shouldn't puke, but has, thus checking"
        self.kls("sys-libs/db:4.4")
        self.kls("%s:azAZ.-+_09" % astr)
        self.kls("%s:_bar" % astr) # According to PMS, underscore and plus-sign are
        self.kls("%s:+bar" % astr) # not invalid first chars in a slot dep
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foo:")
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foo:1,,0")
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foo:1:")
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foo:-1")
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foo:.1")
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foo:1@2")

    def test_slot_operators_and_subslots(self):
        self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:*", eapi=4)
        self.kls("sys-libs/db:*", eapi=5)
        self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:=", eapi=4)
        self.kls("sys-libs/db:=", eapi=5)
        self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:==", eapi=5)
        self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:1=", eapi=4)
        self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:2/3.0=", eapi=4)
        self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:2/3.0", eapi=1)
        self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:/=", eapi=5)
        self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:/1=", eapi=5)
        self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:1/=", eapi=5)
        self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:*1/=", eapi=5)

        for subslot in ("/1.0", ""):
            self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:*4%s" % subslot, eapi=5)
            self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:4%s*" % subslot, eapi=5)
            self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:=4%s" % subslot, eapi=5)
            self.kls("sys-libs/db:4%s=" % subslot, eapi=5)
            self.kls("sys-libs/db:3.2%s=" % subslot, eapi=5)
            self.assertRaises(errors.MalformedAtom, self.kls, "sys-libs/db:4%s==" % subslot, eapi=5)

        def check_it(text, slot, subslot, operator):
            obj = self.kls("sys-libs/db%s" % text)
            self.assertEqual(obj.slot, slot)
            self.assertEqual(obj.subslot, subslot)
            self.assertEqual(obj.slot_operator, operator)
        check_it(":4", "4", None, None)
        check_it(":=", None, None, "=")
        check_it(":4=", "4", None, "=")
        check_it(":4/0.4=", "4", "0.4", "=")
        check_it(":*", None, None, "*")

        # Verify restrictions.
        self.assertMatch(self.kls("sys-libs/db:1="),
            FakePkg("sys-libs/db-1", slot="1"))
        self.assertMatch(self.kls("sys-libs/db:1/2="),
            FakePkg("sys-libs/db-1", slot="1", subslot="2"))
        self.assertNotMatch(self.kls("sys-libs/db:1/2.3="),
            FakePkg("sys-libs/db-1", slot="1", subslot="2"))
        self.assertNotMatch(self.kls("sys-libs/db:1/2.3="),
            FakePkg("sys-libs/db-1", slot="1"))
        self.assertMatch(self.kls("sys-libs/db:1a.2/2.3"),
            FakePkg("sys-libs/db-1", slot="1a.2", subslot="2.3"))

    def test_getattr(self):
        # assert it explodes for bad attr access.
        obj = self.kls("dev-util/diffball")
        self.assertRaises(AttributeError, getattr, obj, "__foasdfawe")
        # assert ordering


        def assertAttr(attr):
            self.assertEqual(restrictions[pos].attr, attr,
                msg="expected attr %r at %i for ver(%s), repo(%s) use(%s), "
                    "slot(%s): got %r from %r" % (attr, pos, ver, repo, use,
                    slot, restrictions[pos].attr, restrictions))
            return pos + 1

        slot = ''
        def f():
            for pref, ver in (('', ''), ('=', '-0.1')):
                for repo in ('', '::gentoo'):
                    for slot in ('', ':1'):
                        for use in ('', '[x]'):
                            yield pref, ver, repo, slot, use

        for pref, ver, repo, slot, use in f():
            pos = 0
            o = self.kls("%sdev-util/diffball%s%s%s%s" %
                (pref, ver, slot, repo, use))
            count = 2
            for x in ("use", "repo", "pref", "slot"):
                if locals()[x]:
                    count += 1

            restrictions = o.restrictions
            self.assertEqual(len(restrictions), count,
                msg="%r, restrictions count must be %i, got %i" %
                    (o, count, len(restrictions)))
            self.assertTrue([getattr(x, 'type', None)
                for x in restrictions], ['package'] * count)
            if repo:
                pos = assertAttr('repo.repo_id')
            pos = assertAttr('package')
            pos = assertAttr('category')
            if ver:
                self.assertInstance(restrictions[pos], restricts.VersionMatch,
                    msg="expected %r, got %r; repo(%s), ver(%s), use(%s) "
                        "slot(%s)" %
                        (restricts.VersionMatch, restrictions[pos],
                            repo, ver, use, slot))
                pos += 1
            if slot:
                pos = assertAttr('slot')
            if use:
                pos = assertAttr('use')

    def test_eapi0(self):
        for postfix in (':1', ':1,2', ':asdf', '::asdf', '::asdf-x86', '[x]',
                        '[x,y]', ':1[x,y]', '[x,y]:1', ':1::repo'):
            self.assertRaisesMsg("dev-util/foon%s must be invalid in EAPI 0"
                % postfix, errors.MalformedAtom, self.kls,
                "dev-util/foon%s" % postfix, eapi=0)

    def test_eapi1(self):
        for postfix in (':1,2', '::asdf', '::asdf-x86', '[x]',
                        '[x,y]', ':1[x,y]', '[x,y]:1', ':1:repo'):
            self.assertRaisesMsg("dev-util/foon%s must be invalid in EAPI 1"
                % postfix, errors.MalformedAtom, self.kls,
                "dev-util/foon%s" % postfix, eapi=1)
        self.kls("dev-util/foon:1", eapi=1)
        self.kls("dev-util/foon:12", eapi=1)
        self.assertRaisesMsg("dev-util/foon[dar] must be invalid in EAPI 1",
            errors.MalformedAtom,
            self.kls, "dev-util/foon[dar]", eapi=1)

    def test_eapi2(self):
        self.check_use(2)

    def test_eapi3(self):
        self.check_use(3)
        self.kls("dev-util/foon:1", eapi=3)
        self.kls("dev-util/foon:2", eapi=3)
        self.kls("!dev-util/foon:1", eapi=3)
        self.kls("dev-util/foon:1[x]", eapi=3)
        self.kls("dev-util/foon:1[x?]", eapi=3)
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foon:1::dar", eapi=3)

    def test_eapi4(self):
        self.check_use(4, defaults=True)

    def test_repo_id(self):
        astr = "dev-util/bsdiff"
        c = FakePkg("%s-1" % astr, repo=FakeRepo(repo_id="gentoo-x86A_"), slot="0")
        self.assertMatch(self.kls("%s" % astr), c)
        self.assertMatch(self.kls("%s::gentoo-x86A_" % astr), c)
        self.assertMatch(self.kls("%s:0::gentoo-x86A_" % astr), c)
        self.assertNotMatch(self.kls("%s::gentoo2" % astr), c)
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foon:1:")
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foon::")
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foon::-gentoo-x86")
        self.assertRaises(errors.MalformedAtom, self.kls, "dev-util/foon:::")
        for x in xrange(0, 3):
            self.assertRaises(errors.MalformedAtom, self.kls,
                "dev-util/foon::gentoo-x86", eapi=x)

    def test_invalid_atom(self):
        self.assertRaises(errors.MalformedAtom, self.kls, '~dev-util/spork')
        self.assertRaises(errors.MalformedAtom, self.kls, '>dev-util/spork')
        self.assertRaises(errors.MalformedAtom, self.kls, 'dev-util/spork-3')
        self.assertRaises(errors.MalformedAtom, self.kls, 'spork')

    def test_intersects(self):
        for this, that, result in [
            ('cat/pkg', 'pkg/cat', False),
            ('cat/pkg', 'cat/pkg', True),
            ('cat/pkg:1', 'cat/pkg:1', True),
            ('cat/pkg:1', 'cat/pkg:2', False),
            ('cat/pkg:1', 'cat/pkg[foo]', True),
            ('cat/pkg[foo]', 'cat/pkg[-bar]', True),
            ('cat/pkg[foo]', 'cat/pkg[-foo]', False),
            ('>cat/pkg-3', '>cat/pkg-1', True),
            ('>cat/pkg-3', '<cat/pkg-3', False),
            ('>=cat/pkg-3', '<cat/pkg-3', False),
            ('>cat/pkg-2', '=cat/pkg-2*', True),
            ('<cat/pkg-2_alpha1', '=cat/pkg-2*', True),
            ('=cat/pkg-2', '=cat/pkg-2', True),
            ('=cat/pkg-3', '=cat/pkg-2', False),
            ('=cat/pkg-2', '>cat/pkg-2', False),
            ('=cat/pkg-2', '>=cat/pkg-2', True),
            ('~cat/pkg-2', '~cat/pkg-2', True),
            ('~cat/pkg-2', '~cat/pkg-2.1', False),
            ('=cat/pkg-2*', '=cat/pkg-2.3*', True),
            ('>cat/pkg-2.4', '=cat/pkg-2*', True),
            ('<cat/pkg-2.4', '=cat/pkg-2*', True),
            ('<cat/pkg-1', '=cat/pkg-2*', False),
            ('~cat/pkg-2', '>cat/pkg-2-r1', True),
            ('~cat/pkg-2', '<=cat/pkg-2', True),
            ('=cat/pkg-2-r2*', '<=cat/pkg-2-r20', True),
            ('=cat/pkg-2-r2*', '<cat/pkg-2-r20', True),
            ('=cat/pkg-2-r2*', '<=cat/pkg-2-r2', True),
            ('~cat/pkg-2', '<cat/pkg-2', False),
            ('=cat/pkg-1-r10*', '~cat/pkg-1', True),
            ('=cat/pkg-1-r1*', '<cat/pkg-1-r1', False),
            ('=cat/pkg-1*', '>cat/pkg-2', False),
            ('>=cat/pkg-8.4', '=cat/pkg-8.3.4*', False),
            ('cat/pkg::gentoo', 'cat/pkg', True),
            ('cat/pkg::gentoo', 'cat/pkg::foo', False),
            # known to cause an assplosion, thus redundant test.
            ('=sys-devel/gcc-4.1.1-r3', '=sys-devel/gcc-3.3*', False),
            ('=sys-libs/db-4*', '~sys-libs/db-4.3.29', True),
            ]:
            this_atom = self.kls(this)
            that_atom = self.kls(that)
            self.assertEqual(
                result, this_atom.intersects(that_atom),
                '%s intersecting %s should be %s' % (this, that, result))
            self.assertEqual(
                result, that_atom.intersects(this_atom),
                '%s intersecting %s should be %s' % (that, this, result))

    def assertEqual2(self, o1, o2):
        # logic bugs hidden behind short circuiting comparisons for metadata
        # is why we test the comparison *both* ways.
        self.assertEqual(o1, o2)
        c = cmp(o1, o2)
        self.assertEqual(c, 0,
            msg="checking cmp for %r, %r, aren't equal: got %i" % (o1, o2, c))
        self.assertEqual(o2, o1)
        c = cmp(o2, o1)
        self.assertEqual(c, 0,
            msg="checking cmp for %r, %r,aren't equal: got %i" % (o2, o1, c))

    def assertNotEqual2(self, o1, o2):
        # is why we test the comparison *both* ways.
        self.assertNotEqual(o1, o2)
        c = cmp(o1, o2)
        self.assertNotEqual(c, 0,
            msg="checking cmp for %r, %r, not supposed to be equal, got %i"
                % (o1, o2, c))
        self.assertNotEqual(o2, o1)
        c = cmp(o2, o1)
        self.assertNotEqual(c, 0,
            msg="checking cmp for %r, %r, not supposed to be equal, got %i"
                % (o2, o1, c))

    def test_comparison(self):
        self.assertEqual2(self.kls('cat/pkg'), self.kls('cat/pkg'))
        self.assertNotEqual2(self.kls('cat/pkg'), self.kls('cat/pkgb'))
        self.assertNotEqual2(self.kls('cata/pkg'), self.kls('cat/pkg'))
        self.assertNotEqual2(self.kls('cat/pkg'), self.kls('!cat/pkg'))
        self.assertEqual2(self.kls('!cat/pkg'), self.kls('!cat/pkg'))
        self.assertNotEqual2(self.kls('=cat/pkg-0.1:0'),
            self.kls('=cat/pkg-0.1'))
        self.assertNotEqual2(self.kls('=cat/pkg-1[foon]'),
            self.kls('=cat/pkg-1'))
        self.assertEqual2(self.kls('=cat/pkg-0'), self.kls('=cat/pkg-0'))
        self.assertNotEqual2(self.kls('<cat/pkg-2'), self.kls('>cat/pkg-2'))
        self.assertNotEqual2(self.kls('=cat/pkg-2*'), self.kls('=cat/pkg-2'))
        self.assertNotEqual2(self.kls('=cat/pkg-2', True),
            self.kls('=cat/pkg-2'))

        # use...
        self.assertNotEqual2(self.kls('cat/pkg[foo]'), self.kls('cat/pkg'))
        self.assertNotEqual2(self.kls('cat/pkg[foo]'),
                             self.kls('cat/pkg[-foo]'))
        self.assertEqual2(self.kls('cat/pkg[foo,-bar]'),
                          self.kls('cat/pkg[-bar,foo]'))
        # repo_id
        self.assertEqual2(self.kls('cat/pkg::a'), self.kls('cat/pkg::a'))
        self.assertNotEqual2(self.kls('cat/pkg::a'), self.kls('cat/pkg::b'))
        self.assertNotEqual2(self.kls('cat/pkg::a'), self.kls('cat/pkg'))

        # slots.
        self.assertNotEqual2(self.kls('cat/pkg:1'), self.kls('cat/pkg'))
        self.assertEqual2(self.kls('cat/pkg:2'), self.kls('cat/pkg:2'))
        for lesser, greater in (('0.1', '1'), ('1', '1-r1'), ('1.1', '1.2')):
            self.assertTrue(self.kls('=d/b-%s' % lesser) <
                self.kls('=d/b-%s' % greater),
                msg="d/b-%s < d/b-%s" % (lesser, greater))
            self.assertFalse(self.kls('=d/b-%s' % lesser) >
                self.kls('=d/b-%s' % greater),
                msg="!: d/b-%s < d/b-%s" % (lesser, greater))
            self.assertTrue(self.kls('=d/b-%s' % greater) >
                self.kls('=d/b-%s' % lesser),
                msg="d/b-%s > d/b-%s" % (greater, lesser))
            self.assertFalse(self.kls('=d/b-%s' % greater) <
                self.kls('=d/b-%s' % lesser),
                msg="!: d/b-%s > d/b-%s" % (greater, lesser))

        self.assertTrue(self.kls("!!=d/b-1", eapi=2) > self.kls("!=d/b-1"))
        self.assertTrue(self.kls("!=d/b-1") < self.kls("!!=d/b-1"))
        self.assertEqual(self.kls("!=d/b-1"), self.kls("!=d/b-1"))

    def test_compatibility(self):
        self.assertNotMatch(self.kls('=dev-util/diffball-0.7'),
            FakePkg('dev-util/diffball-0.7.0'))
        # see bug http://bugs.gentoo.org/152127
        self.assertNotMatch(self.kls('>=sys-apps/portage-2.1.0_pre3-r5'),
            FakePkg('sys-apps/portage-2.1_pre3-r5'))

    def test_combined(self):
        p = FakePkg('dev-util/diffball-0.7', repo=FakeRepo(repo_id='gentoo'))
        self.assertMatch(self.kls('=dev-util/diffball-0.7::gentoo'), p)
        self.assertMatch(self.kls('dev-util/diffball::gentoo'), p)
        self.assertNotMatch(self.kls('=dev-util/diffball-0.7:1::gentoo'),
            FakePkg('dev-util/diffball-0.7', slot='2'))

    def test_unversioned(self):
        self.assertTrue(self.kls("dev-util/diffball").is_simple)
        self.assertFalse(self.kls("dev-util/diffball:2").is_simple)
        self.assertFalse(self.kls("dev-util/diffball:2::gentoo").is_simple)
        self.assertFalse(self.kls("dev-util/diffball::gentoo").is_simple)
        self.assertFalse(self.kls("!=dev-util/diffball-1").is_simple)
        self.assertFalse(self.kls(">dev-util/diffball-1.2").is_simple)
        self.assertFalse(self.kls("=dev-util/diffball-1").is_simple)
        self.assertFalse(self.kls("dev-util/diffball[x]").is_simple)
        self.assertFalse(self.kls("dev-util/diffball[x?]").is_simple)


class Test_cpy_atom(Test_native_atom):

    kls = staticmethod(atom.atom)
    if atom.atom_overrides is atom.native_atom_overrides:
        skip = "extension isn't available"

test_cpy_used = mk_cpy_loadable_testcase('pkgcore.ebuild._atom',
    "pkgcore.ebuild.atom", "atom_overrides", "overrides")
