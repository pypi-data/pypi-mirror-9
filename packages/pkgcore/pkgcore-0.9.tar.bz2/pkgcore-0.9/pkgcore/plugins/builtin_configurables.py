# Copyright: 2011 Brian Harring <ferringb@gmail.com>
# Copyright: 2006 Marien Zwart <marienz@gentoo.org>
# License: BSD/GPL2

from snakeoil.test.mixins import PythonNamespaceWalker


class walker(PythonNamespaceWalker):

    ignore_all_import_failures = True

    def _default_module_blacklister(self, target):
        if target.startswith("pkgcore.test.") or target.startswith('pkgcore.plugins.') \
                or 'pkgcore.test' == target:
            return True
        return PythonNamespaceWalker._default_module_blacklister(self, target)

targets = []
for module in walker().walk_namespace('pkgcore'):
    for name in dir(module):
        obj = getattr(module, name)
        if getattr(obj, 'pkgcore_config_type', None) is not None:
            targets.append('%s.%s' % (module.__name__, name))

pkgcore_plugins = {
    'configurable': targets
}
