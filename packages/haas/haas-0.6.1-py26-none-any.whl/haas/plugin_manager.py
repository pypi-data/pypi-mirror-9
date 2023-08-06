# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

import sys
import logging

if sys.version_info < (2, 7):  # pragma: no cover
    from ordereddict import OrderedDict
else:  # pragma: no cover
    from collections import OrderedDict

from stevedore.extension import ExtensionManager

logger = logging.getLogger(__name__)


class PluginManager(object):

    ENVIRONMENT_HOOK = 'haas.hooks.environment'

    RESULT_HANDLERS = 'haas.result.handler'

    TEST_RUNNER = 'haas.runner'

    TEST_DISCOVERY = 'haas.discovery'

    _help = {
        TEST_DISCOVERY: 'The test discovery implementation to use.',
        TEST_RUNNER: 'Test runner implementation to use.',
        RESULT_HANDLERS: 'Test result handler implementation to use.',
    }

    _namespace_to_option_parts = {
        TEST_DISCOVERY: ['discovery'],
        TEST_RUNNER: ['runner'],
        RESULT_HANDLERS: ['result', 'handler'],
    }

    def __init__(self):
        self.hook_managers = OrderedDict()
        self.hook_managers[self.ENVIRONMENT_HOOK] = ExtensionManager(
            namespace=self.ENVIRONMENT_HOOK,
            invoke_on_load=True,
        )

        self.driver_managers = OrderedDict()
        self.driver_managers[self.TEST_DISCOVERY] = ExtensionManager(
            namespace=self.TEST_DISCOVERY,
        )
        self.driver_managers[self.TEST_RUNNER] = ExtensionManager(
            namespace=self.TEST_RUNNER,
        )
        self.driver_managers[self.RESULT_HANDLERS] = ExtensionManager(
            namespace=self.RESULT_HANDLERS,
        )

    @classmethod
    def testing_plugin_manager(cls, hook_managers, driver_managers):
        """Create a fabricated plugin manager for testing.

        """
        plugin_manager = cls.__new__(cls)
        plugin_manager.hook_managers = OrderedDict(hook_managers)
        plugin_manager.driver_managers = OrderedDict(driver_managers)
        return plugin_manager

    def _filter_enabled_plugins(self, extension):
        if extension.obj.enabled:
            return extension.obj
        return None

    def _add_hook_extension_arguments(self, extension, parser):
        extension.obj.add_parser_arguments(parser)

    def _configure_hook_extension(self, extension, args):
        extension.obj.configure(args)

    def _add_driver_extension_arguments(self, extension, parser, option_prefix,
                                        dest_prefix):
        extension.plugin.add_parser_arguments(
            parser, option_prefix, dest_prefix)

    def _namespace_to_option(self, namespace):
        parts = self._namespace_to_option_parts[namespace]
        option = '--{0}'.format('-'.join(parts))
        dest = '_'.join(parts)
        return option, dest

    def add_plugin_arguments(self, parser):
        """Add plugin arguments to argument parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The main haas ArgumentParser.

        """
        for manager in self.hook_managers.values():
            if len(list(manager)) == 0:
                continue
            manager.map(self._add_hook_extension_arguments, parser)
        for namespace, manager in self.driver_managers.items():
            choices = list(sorted(manager.names()))
            if len(choices) == 0:
                continue
            option, dest = self._namespace_to_option(namespace)
            parser.add_argument(
                option, help=self._help[namespace], dest=dest,
                choices=choices, default='default')
            option_prefix = '{0}-'.format(option)
            dest_prefix = '{0}_'.format(dest)
            manager.map(self._add_driver_extension_arguments,
                        parser, option_prefix, dest_prefix)

    def configure_plugins(self, args):
        """Configure enabled plugins with parsed commandline arguments.

        """
        for manager in self.hook_managers.values():
            if len(list(manager)) == 0:
                continue
            manager.map(self._configure_hook_extension, args)

    def get_enabled_hook_plugins(self, hook):
        """Get enabled plugins for specified hook name.

        """
        manager = self.hook_managers[hook]
        if len(list(manager)) == 0:
            return []
        return [plugin for plugin in manager.map(self._filter_enabled_plugins)
                if plugin is not None]

    def get_driver(self, namespace, parsed_args, **kwargs):
        """Get mutually-exlusive plugin for plugin namespace.

        """
        option, dest = self._namespace_to_option(namespace)
        dest_prefix = '{0}_'.format(dest)
        driver_name = getattr(parsed_args, dest, 'default')
        driver_extension = self.driver_managers[namespace][driver_name]
        return driver_extension.plugin.from_args(
            parsed_args, dest_prefix, **kwargs)
