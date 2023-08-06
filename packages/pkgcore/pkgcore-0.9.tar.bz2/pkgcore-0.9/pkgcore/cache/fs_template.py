# Copyright: 2005-2011 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

"""
template for fs based backends
"""

__all__ = ("FsBased",)

import os

from snakeoil.osutils import ensure_dirs, pjoin

from pkgcore.cache import base
from pkgcore.os_data import portage_gid


class FsBased(base):
    """Template wrapping fs needed options.

    Provides _ensure_access as a way to attempt to ensure files have
    the specified owners/perms.
    """

    def __init__(self, location, label=None, **config):
        """
        throws InitializationError if needs args aren't specified

        :keyword gid: defaults to :obj:`pkgcore.os_data.portage_gid`,
            gid to force all entries to
        :keyword perms: defaults to 0665, mode to force all entries to"""

        for x, y in (("gid", portage_gid), ("perms", 0664)):
            if x in config:
                setattr(self, "_"+x, config[x])
                del config[x]
            else:
                setattr(self, "_"+x, y)
        super(FsBased, self).__init__(**config)

        if label is not None:
            location = pjoin(location, label.lstrip(os.path.sep))

        self.location = location

        self._mtime_used = 'mtime' == self.chf_type

    __init__.__doc__ = "\n".join(
        x.lstrip() for x in __init__.__doc__.split("\n") + [
            y.lstrip().replace("@param", "@keyword")
            for y in base.__init__.__doc__.split("\n")
            if "@param" in y])

    def _ensure_access(self, path, mtime=None):
        """Ensure access to a path.

        :param mtime: if specified change mtime to this value.
        :return: C{False} if unable to guarantee access, C{True} otherwise.
        """
        try:
            os.chown(path, -1, self._gid)
            os.chmod(path, self._perms)
            if mtime is not None:
                mtime = long(mtime)
                os.utime(path, (mtime, mtime))
        except EnvironmentError:
            return False
        return True

    def _ensure_dirs(self, path=None):
        """Make sure a path relative to C{self.location} exists."""
        if path is not None:
            path = pjoin(self.location, os.path.dirname(path))
        else:
            path = self.location
        return ensure_dirs(path, mode=0775, minimal=False)
