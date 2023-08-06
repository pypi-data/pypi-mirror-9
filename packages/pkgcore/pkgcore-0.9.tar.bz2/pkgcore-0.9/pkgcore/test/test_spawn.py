# Copyright: 2006-2009 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

import os
import pwd
import signal

from snakeoil.currying import post_curry
from snakeoil.test.mixins import TempDirMixin

from pkgcore import spawn
from pkgcore.test import TestCase, SkipTest


def capability_based(capable, msg):
    def internal_f(f):
        if not capable():
            f.skip = msg
        return f
    return internal_f


class SpawnTest(TempDirMixin, TestCase):

    def __init__(self, *a, **kw):
        try:
            self.bash_path = spawn.find_binary("bash")
            self.null_file = open("/dev/null", "w")
            self.null = self.null_file.fileno()
        except spawn.CommandNotFound:
            self.skip = "bash wasn't found.  this will be ugly."
        super(SpawnTest, self).__init__(*a, **kw)

    def setUp(self):
        self.orig_env = os.environ["PATH"]
        TempDirMixin.setUp(self)
        os.environ["PATH"] = ":".join([self.dir] + self.orig_env.split(":"))

    def tearDown(self):
        self.null_file.close()
        os.environ["PATH"] = self.orig_env
        TempDirMixin.tearDown(self)

    def generate_script(self, filename, text):
        if not os.path.isabs(filename):
            fp = os.path.join(self.dir, filename)
        with open(fp, "w") as f:
            f.write("#!/bin/bash\n")
            f.write(text)
        os.chmod(fp, 0750)
        self.assertEqual(os.stat(fp).st_mode & 0750, 0750)
        return fp

    def test_get_output(self):
        filename = "pkgcore-spawn-getoutput.sh"
        for r, s, text, args in [
            [0, ["dar\n"], "echo dar\n", {}],
            [0, ["dar"], "echo -n dar", {}],
            [1, ["blah\n", "dar\n"], "echo blah\necho dar\nexit 1", {}],
            [0, [], "echo dar 1>&2", {"fd_pipes": {1: 1, 2: self.null}}]]:

            fp = self.generate_script(filename, text)
            self.assertEqual(
                [r, s],
                spawn.spawn_get_output(fp, spawn_type=spawn.spawn_bash, **args))

        os.unlink(fp)

    @capability_based(spawn.is_sandbox_capable, "sandbox binary wasn't found")
    def test_sandbox(self):
        fp = self.generate_script(
            "pkgcore-spawn-sandbox.sh", "echo $LD_PRELOAD")
        ret = spawn.spawn_get_output(fp, spawn_type=spawn.spawn_sandbox)
        self.assertTrue(
            ret[1], msg="no output; exit code was %s; script "
            "location %s" % (ret[0], fp))
        self.assertIn(
            "libsandbox.so",
            [os.path.basename(x.strip()) for x in ret[1][0].split()])
        os.unlink(fp)


    @capability_based(spawn.is_sandbox_capable, "sandbox binary wasn't found")
    def test_sandbox_empty_dir(self):
        """
        sandbox gets pissy if it's ran from a nonexistent dir

        this verifies our fix works.
        """
        fp = self.generate_script(
            "pkgcore-spawn-sandbox.sh", "echo $LD_PRELOAD")
        dpath = os.path.join(self.dir, "dar")
        os.mkdir(dpath)
        try:
            cwd = os.getcwd()
        except OSError:
            cwd = None
        try:
            os.chdir(dpath)
            os.rmdir(dpath)
            self.assertIn(
                "libsandbox.so",
                [os.path.basename(x.strip()) for x in spawn.spawn_get_output(
                    fp, spawn_type=spawn.spawn_sandbox, cwd='/')[1][0].split()])
            os.unlink(fp)
        finally:
            if cwd is not None:
                os.chdir(cwd)

    @capability_based(spawn.is_fakeroot_capable,
                      "fakeroot binary wasn't found")
    def test_fakeroot(self):
        try:
            l = pwd.getpwnam("nobody")
        except KeyError:
            raise SkipTest(
                "system lacks nobody user, thus can't test fakeroot")
        if 'LD_PRELOAD' in os.environ:
            raise SkipTest(
                "disabling test due to LD_PRELOAD setting, which "
                "fakeroot relies upon")

        nobody_uid = l[2]
        nobody_gid = l[3]

        kw = {}
        if os.getuid() == 0:
            kw = {"uid": l[2], "gid": l[3]}

        fp2 = self.generate_script(
            "pkgcore-spawn-fakeroot2.sh",
            "#!%s\nimport os\ns=os.stat('/tmp')\n"
            "print(s.st_uid)\nprint(s.st_gid)\n" %
            spawn.find_binary("python"))

        fp1 = self.generate_script(
            "pkgcore-spawn-fakeroot.sh",
            "#!%s\nchown %i:%i /tmp;%s;\n" % (
                self.bash_path, nobody_uid, nobody_gid, fp2))

        savefile = os.path.join(self.dir, "fakeroot-savefile")
        self.assertNotEqual(long(os.stat("/tmp").st_uid), long(nobody_uid))
        self.assertEqual(
            [0, ["%s\n" % x for x in (nobody_uid, nobody_gid)]],
            spawn.spawn_get_output(
                [self.bash_path, fp1],
                spawn_type=post_curry(spawn.spawn_fakeroot, savefile), **kw))
        self.assertNotEqual(
            long(os.stat("/tmp").st_uid), long(nobody_uid),
            "bad voodoo; we managed to change /tmp to nobody- "
            "this shouldn't occur!")
        self.assertEqual(
            True, os.path.exists(savefile),
            "no fakeroot file was created, either fakeroot differs or our" +
            " args passed to it are bad")

        # yes this is a bit ugly, but fakeroot requires an arg- so we
        # have to curry it
        self.assertEqual(
            [0, ["%s\n" % x for x in (nobody_uid, nobody_gid)]],
            spawn.spawn_get_output(
                [fp2],
                spawn_type=post_curry(spawn.spawn_fakeroot, savefile), **kw))

        os.unlink(fp1)
        os.unlink(fp2)
        os.unlink(savefile)
    test_fakeroot.skip = "test is flakey w/ recent versions of fakeroot; capabilities unused atm also"

    def test_process_exit_code(self):
        self.assertEqual(0, spawn.process_exit_code(0), "exit code failed")
        self.assertEqual(
            16, spawn.process_exit_code(16 << 8), "signal exit code failed")

    def generate_background_pid(self):
        try:
            return spawn.spawn(["sleep", "60s"], returnpid=True)[0]
        except spawn.CommandNotFound:
            raise SkipTest(
                "can't complete the test, sleep binary doesn't exist")

    def test_spawn_returnpid(self):
        pid = self.generate_background_pid()
        try:
            self.assertEqual(
                None, os.kill(pid, 0),
                "returned pid was invalid, or sleep died")
            self.assertEqual(
                True, pid in spawn.spawned_pids,
                "pid wasn't recorded in global pids")
        finally:
            os.kill(pid, signal.SIGKILL)

    def test_cleanup_pids(self):
        pid = self.generate_background_pid()
        spawn.cleanup_pids([pid])
        self.assertRaises(OSError, os.kill, pid, 0)
        self.assertNotIn(
            pid, spawn.spawned_pids, "pid wasn't removed from global pids")

    def test_bash(self):
        # bash builtin for true without exec'ing true (eg, no path lookup)
        self.assertEqual(0, spawn.spawn_bash(":"))

    def test_umask(self):
        fp = self.generate_script(
            "portage_spawn_umask.sh", "#!%s\numask" % self.bash_path)
        try:
            old_umask = os.umask(0)
            if old_umask == 0:
                # crap.
                desired = 022
                os.umask(desired)
            else:
                desired = 0
            self.assertEqual(
                str(desired).lstrip("0"),
                spawn.spawn_get_output(fp)[1][0].strip().lstrip("0"))
        finally:
            os.umask(old_umask)

