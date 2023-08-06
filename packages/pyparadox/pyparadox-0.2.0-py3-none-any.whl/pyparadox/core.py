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
import subprocess
import glob
import re

GAMES = {"ck2": "Crusader Kings II", "eu4": "Europa Universalis IV"}
EXPANSION_NAMES = ["Charlemagne", "Legacy of Rome", "Rajas of India",
                   "Sons of Abraham", "Sunset Invasion", "The Old Gods",
                   "The Republic", "The Sword of Islam", "Way of Life",
                   "Art of War", "Res Publica", "Wealth of Nations",
                   "El Dorado"]


class Plugin(object):
    """Represents a single plugin (mod/DLC/expansion)."""

    MOD = 0
    DLC = 1
    EXPANSION = 2

    def __init__(self, name, file_name, plugin_type=0, enabled=True):

        self.name = name
        self.file_name = file_name
        self.plugin_type = plugin_type
        self.enabled = enabled


def find_plugins(path, extension, config=None):
    extension = extension.strip(".")
    plugin_paths = glob.glob(os.path.join(path, "*.{}".format(extension)))

    plugins = []

    if config is not None:
        mods = config["mods"]
        excluded_dlcs = config["excluded_dlcs"]
    else:
        mods = []
        excluded_dlcs = []

    for path in plugin_paths:
        file_name = os.path.basename(path)

        with open(path) as fp:
            try:
                name = find_plugin_name(fp.read())
            except ValueError:
                name = file_name

        if extension == "mod":
            plugin_type = Plugin.MOD
            enabled = file_name in mods
        elif extension == "dlc":
            plugin_type = (Plugin.EXPANSION if name in EXPANSION_NAMES else
                           Plugin.DLC)
            enabled = file_name not in excluded_dlcs
        else:
            # Assume it is a mod. This technically should never happen.
            plugin_type = Plugin.MOD
            enabled = file_name in mods

        plugin = Plugin(name, file_name, plugin_type=plugin_type,
                        enabled=enabled)
        plugins.append(plugin)

    return plugins


def find_plugin_name(plugin_contents):
    try:
        return re.search('^name[ \t]*=[ \t]*"(.*)"', plugin_contents,
                         re.MULTILINE).group(1)
    except AttributeError as e:
        raise ValueError("Could not find plugin name",
                         plugin_contents) from e


def make_command(binary_path, mods, excluded_dlcs):
    command = [binary_path]
    command.append("-skiplauncher")
    for mod in mods:
        command.append("-mod={}".format(os.path.join("mod", mod)))
    for dlc in excluded_dlcs:
        command.append("-exclude_dlc={}".format(os.path.join("dlc", dlc)))
    return command


def execute_command(command, synchronous=False):
    if synchronous:
        return subprocess.call(command)
    else:
        return subprocess.Popen(command)
