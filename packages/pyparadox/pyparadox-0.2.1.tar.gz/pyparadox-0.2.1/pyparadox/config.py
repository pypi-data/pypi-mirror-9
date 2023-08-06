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
import sys
import json

import appdirs

DEFAULT_CONFIG_DIR = appdirs.user_config_dir("PyParadox")


def default_values(game):
    mods = []
    excluded_dlcs = []

    if game == "ck2":
        full_game = "Crusader Kings II"
    elif game == "eu4":
        full_game = "Europa Universalis IV"
    else:
        full_game = ""

    # Windows
    if sys.platform.startswith("win"):
        binary_path = os.path.join(os.environ["ProgramFiles(x86)"],
                                   "Steam",
                                   "SteamApps",
                                   "common",
                                   full_game,
                                   "{}.exe".format(game))
        mod_path = os.path.join(os.path.expanduser("~"),
                                "Documents",
                                "Paradox Interactive",
                                full_game,
                                "mod")
    # OS X
    elif sys.platform == 'darwin':
        binary_path = os.path.join(appdirs.user_data_dir("Steam"),
                                   "SteamApps",
                                   "common",
                                   full_game,
                                   game)
        mod_path = os.path.join(os.path.expanduser("~"),
                                "Documents",
                                "Paradox Interactive",
                                full_game,
                                "mod")
    # Linux
    else:
        binary_path = os.path.join(os.path.expanduser("~"),
                                   ".local",
                                   "share",
                                   "Steam",
                                   "steamapps",
                                   "common",
                                   full_game,
                                   game)
        mod_path = os.path.join(os.path.expanduser("~"),
                                ".paradoxinteractive",
                                full_game,
                                "mod")

    return {
        "game": game,
        "mods": mods,
        "excluded_dlcs": excluded_dlcs,
        "binary_path": binary_path,
        "mod_path": mod_path
    }


class JsonBackend:

    @staticmethod
    def read(stream):
        return json.load(stream)

    @staticmethod
    def write(data, stream):
        json.dump(data, stream, indent=4, sort_keys=True)


class Config(dict):

    def __init__(self, *args, **kwargs):
        self.backend = kwargs.pop("backend", JsonBackend)
        super().__init__(*args, **kwargs)

    @staticmethod
    def build_config(stream_or_file, default=None, backend=JsonBackend):
        try:
            stream = open(stream_or_file)
        except TypeError:
            stream = stream_or_file
        except FileNotFoundError:
            stream = None

        if stream:
            data = backend.read(stream)
            stream.close()
        else:
            data = default if default is not None else dict()

        return Config(data, backend=backend)

    def load(self, stream, override=True, suppress_merge=False):
        data = self.backend.read(stream)
        if override:
            self.update(data)
        else:
            for key, value in data.items():
                if key in self:
                    if not suppress_merge:
                        raise AttributeError("key '{}' already exists".format(
                            key))
                else:
                    self[key] = value

    def save(self, stream):
        self.backend.write(self, stream)


class FileConfig(Config):

    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path

    @staticmethod
    def build_config(path, default=None, backend=JsonBackend):
        config = Config.build_config(path, default=default, backend=backend)

        return FileConfig(path, dict(config.items()), backend=backend)

    def load(self, override=True, suppress_merge=True):
        with open(self.path):
            super().load(self.path, override=override,
                         suppress_merge=suppress_merge)

    def save(self):
        _mkdir_p(os.path.dirname(self.path))

        with open(self.path, "w") as fp:
            super().save(fp)


def _mkdir_p(directory):
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass
