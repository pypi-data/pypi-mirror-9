# Copyright: 2005-2011 Brian Harring <ferringb@gmail.com>
# Copyright: 2005-2006 Marien Zwart <marienz@gentoo.org>
# License: BSD/GPL2

"""Collapse multiple config-sources and instantiate from them.

A lot of extra documentation on this is in dev-notes/config.rst.
"""

__all__ = ("CollapsedConfig", "ConfigManager",)

import collections
from itertools import chain
import weakref

from snakeoil import mappings, compatibility, sequences, klass

from pkgcore.config import errors, basics

_section_data = sequences.namedtuple('_section_data', ['name', 'section'])


class _ConfigMapping(mappings.DictMixin):

    """Minimal dict-like wrapper returning config sections by type.

    Similar to :class:`mappings.LazyValDict` but __getitem__
    does not call the key func for __getitem__.

    Careful: getting the keys for this mapping will collapse all of
    central's configs to get at their types, which might be slow if
    any of them are remote!
    """

    def __init__(self, manager, typename):
        mappings.DictMixin.__init__(self)
        self.manager = manager
        self.typename = typename

    def __getitem__(self, key):
        conf = self.manager.collapse_named_section(key, raise_on_missing=False)
        if conf is None or conf.type.name != self.typename:
            raise KeyError(key)
        return conf.instantiate()

    def iterkeys(self):
        for name in self.manager.sections():
            try:
                collapsed = self.manager.collapse_named_section(name)
            except errors.BaseError:
                # Cannot be collapsed, ignore it (this is not
                # an error, it can be used as base for
                # something that can be collapsed)
                pass
            else:
                if collapsed.type.name == self.typename:
                    yield name

    def __contains__(self, key):
        conf = self.manager.collapse_named_section(key, raise_on_missing=False)
        return conf is not None and conf.type.name == self.typename


class _ConfigStack(collections.defaultdict):

    def __init__(self):
        collections.defaultdict.__init__(self, list)

    def render_vals(self, manager, key, type_name):
        for data in self.get(key, ()):
            if key in data.section:
                yield data.section.render_value(manager, key, type_name)

    def render_val(self, manager, key, type_name):
        for val in self.render_vals(manager, key, type_name):
            return val
        return None

    def render_prepends(self, manager, key, type_name, flatten=True):
        results = []
        # keep in mind that the sequence we get is a top -> bottom walk of the config
        # as such for this operation we have to reverse it when building the content-
        # specifically, reverse the ordering, but not the content of each item.
        data = []
        for content in self.render_vals(manager, key, type_name):
            data.append(content)
            if content[1]:
                break

        for prepend, this_content, append in reversed(data):
            if this_content:
                results = [this_content]
            if prepend:
                results = [prepend] + results
            if append:
                results += [append]

        if flatten:
            results = chain.from_iterable(results)
        return list(results)


class CollapsedConfig(object):

    """A collapsed config section.

    :type type: :obj:`basics.ConfigType`
    :ivar type: Our type.
    :type config: dict
    :ivar config: The supplied configuration values.
    :ivar debug: if True exception wrapping is disabled.
    :ivar default: True if this section is a default.
    :type name: C{str} or C{None}
    :ivar name: our section name or C{None} for an anonymous section.
    """

    def __init__(self, type_obj, config, manager, debug=False, default=False):
        """Initialize instance vars."""
        # Check if we got all values required to instantiate.
        missing = set(type_obj.required) - set(config)
        if missing:
            raise errors.ConfigurationError(
                'type %s.%s needs settings for %s' % (
                    type_obj.callable.__module__,
                    type_obj.callable.__name__,
                    ', '.join(repr(var) for var in missing)))

        self.name = None
        self.default = default
        self.debug = debug
        self.type = type_obj
        self.config = config
        # Cached instance if we have one.
        self._instance = None
        if manager is not None:
            manager = weakref.ref(manager)
        self.manager = manager

    def instantiate(self):
        if self._instance is None:
            try:
                self._instance = self._instantiate()
            except compatibility.IGNORED_EXCEPTIONS:
                raise
            except Exception as e:
                compatibility.raise_from(errors.InstantiationError(self.name))
        return self._instance

    def _instantiate(self):
        """Call our type's callable, cache and return the result.

        Calling instantiate more than once will return the cached value.
        """

        # Needed because this code can run twice even with instance
        # caching if we trigger an ComplexInstantiationError.
        config = mappings.ProtectedDict(self.config)

        # Instantiate section refs.
        # Careful: not everything we have for needs to be in the conf dict
        # (because of default values) and not everything in the conf dict
        # needs to have a type (because of allow_unknowns).
        for name, val in config.iteritems():
            typename = self.type.types.get(name)
            if typename is None:
                continue
            # central already checked the type, no need to repeat that here.
            unlist_it = False
            if typename.startswith('ref:'):
                val = [val]
                unlist_it = True
            if typename.startswith('refs:') or unlist_it:
                try:
                    final_val = []
                    for ref in val:
                        final_val.append(ref.instantiate())
                except compatibility.IGNORED_EXCEPTIONS:
                    raise
                except Exception as e:
                    compatibility.raise_from(errors.ConfigurationError(
                        "Instantiating reference %r pointing at %r" % (name, ref.name)))
                if unlist_it:
                    final_val = final_val[0]
                config[name] = final_val


        if self.type.requires_config:
            if self.manager is None:
                raise Exception("configuration internal error; "
                    "requires_config is enabled "
                    "but we have no config manager to return ")
            manager = self.manager()
            if manager is None:
                raise Exception("Configuration internal error, potentially "
                    "client code error; manager requested, but the config "
                    "manager is no longer in memory")

            config[self.type.requires_config] = manager

        callable_obj = self.type.callable

        pargs = []
        for var in self.type.positional:
            pargs.append(config.pop(var))
        # Python is basically the worst language ever:
        # TypeError: repo() argument after ** must be a dictionary
        configdict = dict(config)
        try:
            self._instance = callable_obj(*pargs, **configdict)
        except compatibility.IGNORED_EXCEPTIONS:
            raise
        except Exception as e:
            compatibility.raise_from(errors.InstantiationError(self.name,
                "exception caught from %r" % (errors._identify_functor_source(self.type.callable),)))
        if self._instance is None:
            raise errors.ComplexInstantiationError(
                'No object returned', callable_obj=callable_obj, pargs=pargs,
                kwargs=configdict)

        return self._instance


_singleton = object()

class _ConfigObjMap(object):

    def __init__(self, manager):
        self._manager = manager

    def __getattr__(self, attr):
        return _ConfigMapping(self._manager, attr)

    def __getitem__(self, key):
        val = getattr(self._manager.objects, key, _singleton)
        if val is None:
            raise KeyError(key)
        return val


class CompatConfigManager(object):

    def __init__(self, manager):
        self._manager = manager

    def __getattr__(self, attr):
        obj = getattr(self._manager, attr, _singleton)
        if obj is _singleton:
            obj = getattr(self._manager.objects, attr)
        return obj


class ConfigManager(object):

    """Combine config type definitions and configuration sections.

    Creates instances of a requested type and name by pulling the
    required data from any number of provided configuration sources.

    The following special type names are recognized:
      - configsection: instantiated and used the same way as an entry in the
        configs :obj:`__init__` arg.

    These "magic" typenames are only recognized if they are used by a
    section with a name starting with "autoload".
    """

    def __init__(self, configs=(), debug=False):
        """Initialize.

        :type configs: sequence of mappings of string to ConfigSection.
        :param configs: configuration to use.
            Can define extra configs that are also loaded.
        :param debug: if set to True exception wrapping is disabled.
            This means things can raise other exceptions than
            ConfigurationError but tracebacks are complete.
        """
        self.original_config_sources = tuple(map(self._compat_mangle_config, configs))
        # Set of encountered section names, used to catch recursive references.
        self._refs = set()
        self.debug = debug
        self.reload()
        # cycle...
        self.objects = _ConfigObjMap(self)

    def _compat_mangle_config(self, config):
        if hasattr(config, 'sections'):
            return config
        return basics.GeneratedConfigSource(config, "unknown")

    def reload(self):
        """Reinitialize us from the config sources originally passed in.

        This throws away all cached instances and re-executes autoloads.
        """
        # "Attribute defined outside __init__"
        # pylint: disable-msg=W0201
        self.configs = []
        self.config_sources = []
        # Cache mapping confname to CollapsedConfig.
        self.rendered_sections = {}
        self.sections_lookup = collections.defaultdict(collections.deque)
        # force regeneration.
        self._types = klass._uncached_singleton
        for config in self.original_config_sources:
            self.add_config_source(config)

    def add_config_source(self, config):
        return self._add_config_source(self._compat_mangle_config(config))

    def _add_config_source(self, config):
        """Pull extra type and config sections from configs and use them.

        Things loaded this way are added after already loaded things
        (meaning the config containing the autoload section overrides
        the config(s) added by that section).
        """
        config_data = config.sections()

        collision = set(self.rendered_sections)
        collision.intersection_update(config_data)

        if collision:
            # If this matches something we previously instantiated
            # we should probably blow up to prevent massive
            # amounts of confusion (and recursive autoloads)
            raise errors.ConfigurationError("New config is trying to "
                "modify existing section(s) %s that was already instantiated."
                % (', '.join(repr(x) for x in sorted(collision)),))


        self.configs.append(config_data)
        self.config_sources.append(config)
        for name in config_data:
            self.sections_lookup[name].appendleft(config_data[name])

            # Do not even touch the ConfigSection if it's not an autoload.
            if not name.startswith('autoload'):
                continue

            try:
                collapsed = self.collapse_named_section(name)
            except compatibility.IGNORED_EXCEPTIONS:
                raise
            except Exception:
                compatibility.raise_from(errors.ConfigurationError(
                    "Failed collapsing autoload section %r" % (name,)))

            if collapsed.type.name != 'configsection':
                raise errors.ConfigurationError(
                   'Section %r is marked as autoload but type is %s, not '
                   'configsection' % (name, collapsed.type.name))
            try:
                instance = collapsed.instantiate()
            except compatibility.IGNORED_EXCEPTIONS:
                compatibility.raise_from(errors.AutoloadInstantiationError(name))
            except Exception:
                compatibility.raise_from(errors.AutoloadInstantiationError(name))
            if collapsed.type.name == 'configsection':
                self.add_config_source(instance)

    def sections(self):
        """Return an iterator of all section names."""
        return self.sections_lookup.iterkeys()

    def collapse_named_section(self, name, raise_on_missing=True):
        """Collapse a config by name, possibly returning a cached instance.

        @returns: :obj:`CollapsedConfig`.

        If there is no section with this name a ConfigurationError is raised,
        unless raise_on_missing is False in which case None is returned.
        """
        if name in self._refs:
            raise errors.ConfigurationError(
                'Reference to %r is recursive' % (name,))
        self._refs.add(name)
        try:
            result = self.rendered_sections.get(name)
            if result is not None:
                return result
            section_stack = self.sections_lookup.get(name)
            if section_stack is None:
                if not raise_on_missing:
                    return None
                if name == "portdir":
                    # gentoo-related usability --jokey
                    raise errors.ConfigurationError(
                        "no section called %r, maybe you didn't add autoload-portage to your file" % (name,))
                raise errors.ConfigurationError(
                   'no section called %r' % (name,))
            try:
                result = self.collapse_section(section_stack, name)
                result.name = name
            except compatibility.IGNORED_EXCEPTIONS:
                raise
            except Exception:
                compatibility.raise_from(errors.ConfigurationError(
                    "Collapsing section named %r" % (name,)))
            self.rendered_sections[name] = result
            return result
        finally:
            self._refs.remove(name)

    def _get_inherited_sections(self, name, sections):
        # List of (name, ConfigSection, index) tuples, most specific first.
        slist = [(name, sections)]

        # first map out inherits.
        inherit_names = set([name])
        for current_section, section_stack in slist:
            current_conf = section_stack[0]
            if 'inherit' not in current_conf:
                continue
            prepend, inherits, append = current_conf.render_value(
                self, 'inherit', 'list')
            if prepend is not None or append is not None:
                raise errors.ConfigurationError(
                    'Prepending or appending to the inherit list makes no '
                    'sense')
            for inherit in inherits:
                if inherit == current_section:
                    # self-inherit.  Mkae use of section_stack to handle this.
                    if len(section_stack) == 1:
                        # nothing else to self inherit.
                        raise errors.ConfigurationError(
                            'Self-inherit %r cannot be found' % (inherit,))
                    if isinstance(section_stack, collections.deque):
                        slist.append((inherit, list(section_stack)[1:]))
                    else:
                        slist.append((inherit, section_stack[1:]))
                else:
                    if inherit in inherit_names:
                        raise errors.ConfigurationError(
                            'Inherit %r is recursive' % (inherit,))
                    inherit_names.add(inherit)
                    target = self.sections_lookup.get(inherit)
                    if target is None:
                        raise errors.ConfigurationError(
                            'inherit target %r cannot be found' % (inherit,))
                    slist.append((inherit, target))
        return [_section_data(name, stack[0]) for (name, stack) in slist]

    def _section_is_inherit_only(self, section):
        if 'inherit-only' in section:
            if section.render_value(self, 'inherit-only', 'bool'):
                return True
        return False

    def collapse_section(self, sections, _name=None):
        """Collapse a ConfigSection to a :obj:`CollapsedConfig`."""

        if self._section_is_inherit_only(sections[0]):
            if sections[0].render_value(self, 'inherit-only', 'bool'):
                raise errors.CollapseInheritOnly(
                    'cannot collapse inherit-only section')

        relevant_sections = self._get_inherited_sections(_name, sections)

        config_stack = _ConfigStack()
        for data in relevant_sections:
            for key in data.section.keys():
                config_stack[key].append(data)

        kls = config_stack.render_val(self, 'class', 'callable')
        if kls is None:
            raise errors.ConfigurationError('no class specified')
        type_obj = basics.ConfigType(kls)
        is_default = bool(config_stack.render_val(self, 'default', 'bool'))

        for key in ('inherit', 'inherit-only', 'class', 'default'):
            config_stack.pop(key, None)

        collapsed = CollapsedConfig(type_obj, self._render_config_stack(type_obj, config_stack),
            self, default=is_default, debug=self.debug)
        return collapsed

    @klass.jit_attr
    def types(self):
        type_map = collections.defaultdict(dict)
        for name, sections in self.sections_lookup.iteritems():
            if self._section_is_inherit_only(sections[0]):
                continue
            obj = self.collapse_named_section(name)
            type_map[obj.type.name][name] = obj
        return mappings.ImmutableDict((k, mappings.ImmutableDict(v))
            for k,v in type_map.iteritems())

    def _render_config_stack(self, type_obj, config_stack):
        conf = {}
        for key in config_stack:
            typename = type_obj.types.get(key)
            if typename is None:
                if not type_obj.allow_unknowns:
                    raise errors.ConfigurationError(
                        'Type of %r unknown' % (key,))
                typename = 'str'

            is_ref = typename.startswith('ref:')
            is_refs = typename.startswith('refs:')

            if typename.startswith('lazy_'):
                typename = typename[5:]

            if typename.startswith('refs:') or typename in ('list', 'str'):
                result = config_stack.render_prepends(self, key, typename, flatten=(typename != 'str'))
                if typename == 'str':
                    result = ' '.join(result)
            else:
                result = config_stack.render_val(self, key, typename)

            if is_ref:
                result = [result]
                is_refs = True

            if is_refs:
                try:
                    result = [ref.collapse() for ref in result]
                except compatibility.IGNORED_EXCEPTIONS:
                    raise
                except Exception:
                    compatibility.raise_from(errors.ConfigurationError(
                        "Failed collapsing section key %r" % (key,)))
            if is_ref:
                result = result[0]

            conf[key] = result

        # Check if we got all values required to instantiate.
        missing = set(type_obj.required) - set(conf)
        if missing:
            raise errors.ConfigurationError(
                'type %s.%s needs settings for %s' % (
                    type_obj.callable.__module__,
                    type_obj.callable.__name__,
                    ', '.join(repr(var) for var in missing)))

        return mappings.ImmutableDict(conf)

    def get_default(self, type_name):
        """Finds the configuration specified default obj of type_name.

        Returns C{None} if no defaults.
        """
        try:
            defaults = self.types.get(type_name, {}).iteritems()
        except compatibility.IGNORED_EXCEPTIONS:
            raise
        except Exception:
            compatibility.raise_from(errors.ConfigurationError(
                "Collapsing defaults for %r" % (type_name,)))
        defaults = [(name, section) for name, section in defaults if section.default]

        if not defaults:
            return None

        if len(defaults) > 1:
            defaults = sorted([x[0] for x in defaults])
            raise errors.ConfigurationError(
                'type %s incorrectly has multiple default sections: %s'
                    % (type_name, ', '.join(map(repr, defaults))))

        try:
            return defaults[0][1].instantiate()
        except compatibility.IGNORED_EXCEPTIONS:
            raise
        except Exception:
            compatibility.raise_from(errors.ConfigurationError(
                "Failed instantiating default %s %r" % (type_name, defaults[0][0])))
        return None
