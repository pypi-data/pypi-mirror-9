# -*- coding: utf-8 -*-
#
# PyParadox is a nix launcher for Paradox titles.
# Copyright (C) 2014  Carmen Bianca Bakker <carmenbbakker@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import time
import textwrap
import unittest
from unittest import mock

from pyparadox import core

_CURRENT_DIRECTORY = os.path.dirname(__file__)
_MOD_DIRECTORY = os.path.join(_CURRENT_DIRECTORY, "fake-mod")
_GAME_DIRECTORY = os.path.join(_CURRENT_DIRECTORY, "fake-game")
_DLC_DIRECTORY = os.path.join(_GAME_DIRECTORY, "dlc")
_CONFIG_DIRECTORY = os.path.join(_CURRENT_DIRECTORY, "fake-config")


class TestCore(unittest.TestCase):

    def test_find_plugins_mod(self):
        plugins = core.find_plugins(_MOD_DIRECTORY, "mod")

        self.assertEqual(len(plugins), 1)

        plugin = plugins[0]

        self.assertEqual(plugin.name, "Better gender law mod")
        self.assertEqual(plugin.file_name, "better gender law mod.mod")
        self.assertEqual(plugin.plugin_type, core.Plugin.MOD)
        self.assertEqual(plugin.enabled, False)

    def test_find_plugins_mod_enabled(self):
        config_dict = {"mods": ["better gender law mod.mod"]}
        config = mock.MagicMock()
        config.__getitem__.side_effect = lambda key: config_dict.get(key)

        plugins = core.find_plugins(_MOD_DIRECTORY, "mod", config=config)

        plugin = plugins[0]

        self.assertTrue(plugin.enabled)

    def test_find_plugins_mod_disabled(self):
        config_dict = {"mods": []}
        config = mock.MagicMock()
        config.__getitem__.side_effect = lambda key: config_dict.get(key)

        plugins = core.find_plugins(_MOD_DIRECTORY, "mod", config=config)

        plugin = plugins[0]

        self.assertFalse(plugin.enabled)

    def test_find_plugins_dlc(self):
        plugins = core.find_plugins(_DLC_DIRECTORY, "dlc")

        self.assertEqual(len(plugins), 2)

        plugins = sorted(plugins, key=lambda x: x.file_name)

        dlc = plugins[0]
        expansion = plugins[1]

        self.assertEqual(dlc.name, "Dynasty Coat of Arms Pack 1")
        self.assertEqual(dlc.file_name, "dlc001.dlc")
        self.assertEqual(dlc.plugin_type, core.Plugin.DLC)
        self.assertEqual(dlc.enabled, True)

        self.assertEqual(expansion.name, "Way of Life")
        self.assertEqual(expansion.file_name, "dlc050.dlc")
        self.assertEqual(expansion.plugin_type, core.Plugin.EXPANSION)
        self.assertEqual(expansion.enabled, True)

    def test_find_plugins_dlc_enabled(self):
        config_dict = {"excluded_dlcs": []}
        config = mock.MagicMock()
        config.__getitem__.side_effect = lambda key: config_dict.get(key)

        plugins = core.find_plugins(_DLC_DIRECTORY, "dlc", config=config)

        for plugin in plugins:
            self.assertTrue(plugin.enabled)

    def test_find_plugins_dlc_disabled(self):
        config_dict = {"excluded_dlcs": ["dlc001.dlc", "dlc050.dlc"]}
        config = mock.MagicMock()
        config.__getitem__.side_effect = lambda key: config_dict.get(key)

        plugins = core.find_plugins(_DLC_DIRECTORY, "dlc", config=config)

        for plugin in plugins:
            self.assertFalse(plugin.enabled)

    def test_find_plugin_name(self):
        string = textwrap.dedent("""\
            name = "foo"
            archive = "bar/bar42.zip"
            steam_id = "1337"
            gamersgate_id = "404"
            checksum = "longstringoftext"
            affects_checksum = no""")

        name = core.find_plugin_name(string)

        self.assertEqual(name, "foo")

    def test_find_plugin_name_not_found(self):
        string = textwrap.dedent("""\
            naaaaaame = "foo"
            archive = "bar/bar42.zip"
            steam_id = "1337"
            gamersgate_id = "404"
            checksum = "longstringoftext"
            affects_checksum = no""")

        with self.assertRaises(ValueError):
            core.find_plugin_name(string)

    def test_make_command(self):
        binary_path = "bin"
        mods = ["mod1", "mod2"]
        excluded_dlcs = ["dlc1", "dlc2"]

        command = core.make_command(binary_path, mods, excluded_dlcs)

        expected = ["bin", "-skiplauncher", "-mod=mod/mod1", "-mod=mod/mod2",
                    "-exclude_dlc=dlc/dlc1", "-exclude_dlc=dlc/dlc2"]

        self.assertEqual(command, expected)

    def test_make_command_plain(self):
        binary_path = "bin"

        command = core.make_command(binary_path, [], [])

        expected = ["bin", "-skiplauncher"]

        self.assertEqual(command, expected)

    def test_execute_command(self):
        start = time.time()

        process = core.execute_command(
            [os.path.join(_GAME_DIRECTORY, "game")])

        end = time.time()
        diff = end - start

        self.assertLess(diff, 0.1)
        self.assertTrue(process)

    def test_execute_command_synchronous(self):
        start = time.time()

        output = core.execute_command(
            [os.path.join(_GAME_DIRECTORY, "game")],
            synchronous=True)

        end = time.time()
        diff = end - start

        self.assertGreaterEqual(diff, 0.1)
        self.assertEqual(output, 0)


if __name__ == "__main__":
    unittest.main()
