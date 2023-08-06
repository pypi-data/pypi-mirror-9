# Copyright: 2006-2011 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD


__all__ = (
    "syncer_exception", "uri_exception", "generic_exception",
    "missing_local_user", "missing_binary", "syncer", "ExternalSyncer",
    "dvcs_syncer", "GenericSyncer", "DisabledSyncer",
    "AutodetectSyncer",
)

from snakeoil import compatibility
from snakeoil.demandload import demandload

from pkgcore.config import ConfigHint, configurable

demandload(
    'os',
    'pwd',
    'stat',
    'errno',
    'pkgcore:os_data,plugin,spawn',
)


class syncer_exception(Exception):
    pass

class uri_exception(syncer_exception):
    pass

class generic_exception(syncer_exception):
    pass

class missing_local_user(syncer_exception):
    pass

class missing_binary(syncer_exception):
    pass


class syncer(object):

    forcable = False

    supported_uris = ()

    # plugin system uses this.
    disabled = False

    pkgcore_config_type = ConfigHint(
        {'path':'str', 'uri':'str'}, typename='syncer')

    @classmethod
    def is_usable_on_filepath(cls, path):
        return None

    def __init__(self, path, uri, default_verbosity=0):
        self.verbose = default_verbosity
        self.basedir = path.rstrip(os.path.sep) + os.path.sep
        self.local_user, self.uri = self.split_users(uri)

    @staticmethod
    def split_users(raw_uri):
        """
        :param raw_uri: string uri to split users from; harring::ferringb:pass
          for example is local user 'harring', remote 'ferringb',
          password 'pass'
        :return: (local user, remote user, remote pass), defaults to root_uid
          if no local user specified
        """
        uri = raw_uri.split("::", 1)
        if len(uri) == 1:
            return os_data.root_uid, raw_uri
        try:
            if uri[1].startswith("@"):
                uri[1] = uri[1][1:]
            if '/' in uri[0] or ':' in uri[0]:
                proto = uri[0].split("/", 1)
                proto[1] = proto[1].lstrip("/")
                uri[0] = proto[1]
                uri[1] = "%s//%s" % (proto[0], uri[1])

            return pwd.getpwnam(uri[0]).pw_uid, uri[1]
        except KeyError as e:
            raise missing_local_user(raw_uri, uri[0], e)

    def sync(self, verbosity=None, force=False):
        if self.disabled:
            return False
        kwds = {}
        if self.forcable and force:
            kwds["force"] = True
        if verbosity is None:
            verbosity = self.verbose
        # output_fd is harded coded as stdout atm.
        return self._sync(verbosity, 1, **kwds)

    def _sync(self, verbosity, output_fd, **kwds):
        raise NotImplementedError(self, "_sync")

    def __str__(self):
        return "%s syncer: %s, %s" % (self.__class__,
            self.basedir, self.uri)

    @classmethod
    def supports_uri(cls, uri):
        for prefix, level in cls.supported_uris:
            if uri.startswith(prefix):
                return level
        return 0


class ExternalSyncer(syncer):

    """Base class for syncers that spawn a binary to do the the actual work."""

    sets_env = False
    binary = None

    def __init__(self, path, uri, default_verbosity=0):
        syncer.__init__(self, path, uri, default_verbosity=default_verbosity)

        if not self.sets_env:
            self.env = {}
        self.env['SSH_AUTH_SOCK'] = os.getenv('SSH_AUTH_SOCK', '')

        if not hasattr(self, 'binary_path'):
            self.binary_path = self.require_binary(self.binary)

    @staticmethod
    def require_binary(bin_name, fatal=True):
        try:
            return spawn.find_binary(bin_name)
        except spawn.CommandNotFound as e:
            if fatal:
                raise missing_binary(bin_name, e)
            return None

    @classmethod
    def _plugin_disabled_check(cls):
        disabled = getattr(cls, '_disabled', None)
        if disabled is None:
            path = getattr(cls, 'binary_path', None)
            if path is None:
                if cls.binary is None:
                    disabled = cls._disabled = True
                else:
                    disabled = cls._disabled = (
                        cls.require_binary(cls.binary, fatal=False) is None)
            else:
                disabled = cls._disabled = os.path.exists(path)
        return disabled

    def set_binary_path(self):
        self.binary_path = self.require_binary(self.binary)

    def _spawn(self, command, pipes, **kwargs):
        return spawn.spawn(command, fd_pipes=pipes, uid=self.local_user,
            env=self.env, **kwargs)

    @staticmethod
    def _rewrite_uri_from_stat(path, uri):
        chunks = uri.split("//", 1)
        if len(chunks) == 1:
            return uri
        try:
            return "%s//%s::%s" % (chunks[0],
                 pwd.getpwuid(os.stat(path).st_uid)[0],
                 chunks[1])
        except KeyError:
            # invalid uid, reuse the uri
            return uri


class dvcs_syncer(ExternalSyncer):

    def _sync(self, verbosity, output_fd):
        try:
            st = os.stat(self.basedir)
        except EnvironmentError as ie:
            if ie.errno != errno.ENOENT:
                compatibility.raise_from(generic_exception(self, self.basedir, ie))
            command = self._initial_pull()
            chdir = None
        else:
            if not stat.S_ISDIR(st.st_mode):
                raise generic_exception(self, self.basedir,
                    "isn't a directory")
            command = self._update_existing()
            chdir = self.basedir

        ret = self._spawn(command, {1:output_fd, 2:output_fd, 0:0},
            cwd=chdir)
        return ret == 0

    def _initial_pull(self):
        raise NotImplementedError(self, "_initial_pull")

    def _update_existing(self):
        raise NotImplementedError(self, "_update_existing")

@configurable({'basedir':'str', 'uri':'str'}, typename='syncer')
def GenericSyncer(basedir, uri, default_verbosity=0):
    """Syncer using the plugin system to find a syncer based on uri."""
    plugins = list(
        (plug.supports_uri(uri), plug)
        for plug in plugin.get_plugins('syncer'))
    plugins.sort(key=lambda x:x[0])
    if not plugins or plugins[-1][0] <= 0:
        raise uri_exception('no known syncer supports %r' % (uri,))
    # XXX this is random if there is a tie. Should we raise an exception?
    return plugins[-1][1](basedir, uri, default_verbosity=default_verbosity)


class DisabledSyncer(syncer):

    def __init__(self, basedir, default_verbosity=0):
        syncer.__init__(self, basedir, '', default_verbosity=default_verbosity)

    @staticmethod
    def disabled():
        return True


@configurable({'basedir':'str'}, typename='syncer')
def AutodetectSyncer(basedir, default_verbosity=0):
    for plug in plugin.get_plugins('syncer'):
        ret = plug.is_usable_on_filepath(basedir)
        if ret is not None:
            return plug(basedir, default_verbosity=default_verbosity, *ret)
    return DisabledSyncer(basedir, '')

