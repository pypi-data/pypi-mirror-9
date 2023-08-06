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
import io
import re
import unittest
from unittest import mock
from unittest.mock import patch, mock_open

from pyparadox.config import Config, FileConfig, JsonBackend

_CURRENT_DIRECTORY = os.path.dirname(__file__)
_MOD_DIRECTORY = os.path.join(_CURRENT_DIRECTORY, "fake-mod")
_GAME_DIRECTORY = os.path.join(_CURRENT_DIRECTORY, "fake-game")
_CONFIG_DIRECTORY = os.path.join(_CURRENT_DIRECTORY, "fake-config")
_CONFIG_PATH = os.path.join(_CONFIG_DIRECTORY, "pyparadox.json")


class TestJsonBackend(unittest.TestCase):

    valid_json = {
        '{}': {},
        '{"Foo": "bar"}': {"Foo": "bar"},
        '{"Foo": [1, 2, 3]}': {"Foo": [1, 2, 3]},
        '{"Foo": null}': {"Foo": None}
    }

    def test_read(self):
        for key, value in self.valid_json.items():
            stream = io.StringIO(key)
            self.assertEqual(JsonBackend.read(stream), value)
            self.assertFalse(stream.closed)
            stream.close()

    def test_write(self):
        for key, value in self.valid_json.items():
            stream = io.StringIO()
            JsonBackend.write(value, stream)
            self.assertEqual(re.sub(r"\s+", "", stream.getvalue()),
                             re.sub(r"\s+", "", key))
            self.assertFalse(stream.closed)
            stream.close()


class TestConfig(unittest.TestCase):

    def test_build_config_stream(self):
        backend = mock.Mock()
        backend.read.side_effect = lambda stream: {"foo": "bar"}
        with io.StringIO() as stream:
            config = Config.build_config(stream, backend=backend)

        self.assertEqual(dict(config.items()), {"foo": "bar"})

    def test_build_config_file(self):
        config_open = mock_open(read_data="valid json here")
        backend = mock.Mock()
        backend.read.side_effect = lambda stream: {"foo": "bar"}

        with patch("pyparadox.config.open", config_open, create=True):
            config = Config.build_config("/fake/path", backend=backend)

        self.assertEqual(dict(config.items()), {"foo": "bar"})
        config_open.assert_called_once_with("/fake/path")

    def test_build_config_default_file_exists(self):
        backend = mock.Mock()
        backend.read.side_effect = lambda stream: {"foo": "bar"}
        with io.StringIO() as stream:
            config = Config.build_config(stream, default={"spam": "eggs"},
                                         backend=backend)

        self.assertEqual(dict(config.items()), {"foo": "bar"})

    def test_build_config_default_file_not_exists(self):
        config_open = mock.Mock()
        config_open.side_effect = FileNotFoundError

        with patch("pyparadox.config.open", config_open, create=True):
            config = Config.build_config("/fake/path", default={"foo": "bar"})

        self.assertEqual(dict(config.items()), {"foo": "bar"})

    def test_load(self):
        backend = mock.Mock()
        backend.read.side_effect = lambda stream: {"foo": "bar"}

        config = Config(backend=backend)
        with io.StringIO() as stream:
            config.load(stream)
            self.assertEqual(dict(config.items()), {"foo": "bar"})

    def test_load_no_override_no_conflict(self):
        backend = mock.Mock()
        backend.read.side_effect = lambda stream: {"foo": "bar"}

        config = Config({"spam": "eggs"}, backend=backend)
        with io.StringIO() as stream:
            config.load(stream, override=False)
            self.assertEqual(sorted(list(config.keys())), ["foo", "spam"])

    def test_load_no_override_with_conflict(self):
        backend = mock.Mock()
        backend.read.side_effect = lambda stream: {"foo": "bar"}

        config = Config({"foo": "spam"}, backend=backend)
        with io.StringIO() as stream:
            with self.assertRaises(AttributeError):
                config.load(stream, override=False)

    def test_load_no_override_with_conflict_suppressed(self):
        backend = mock.Mock()
        backend.read.side_effect = lambda stream: {"foo": "bar"}

        config = Config({"foo": "spam"}, backend=backend)
        with io.StringIO() as stream:
            config.load(stream, override=False, suppress_merge=True)
            self.assertEqual(config["foo"], "spam")

    def test_save(self):
        backend = mock.Mock()

        config = Config(backend=backend)
        stream = mock.Mock()
        config.save(stream)

        backend.write.assert_called_once_with(dict(config.items()), stream)


class TestFileConfig(unittest.TestCase):

    def test_build_config(self):
        config_open = mock_open(read_data="valid json here")
        backend = mock.Mock()
        backend.read.side_effect = lambda stream: {"foo": "bar"}

        with patch("pyparadox.config.open", config_open, create=True):
            config = FileConfig.build_config("/fake/path", backend=backend)

        self.assertEqual(dict(config.items()), {"foo": "bar"})

    def test_load(self):
        config_open = mock_open(read_data="valid json here")
        backend = mock.Mock()
        backend.read.side_effect = lambda stream: {"foo": "bar"}

        config = FileConfig("/fake/path", backend=backend)
        with patch("pyparadox.config.open", config_open, create=True):
            config.load()

        self.assertEqual(dict(config.items()), {"foo": "bar"})

    @patch("pyparadox.config.os.makedirs", autospec=True)
    def test_save(self, config_makedirs):
        config_open = mock_open()
        backend = mock.Mock()

        config = FileConfig("/fake/path", backend=backend)
        with patch("pyparadox.config.open", config_open, create=True):
            config.save()

        backend.write.assert_called_once_with(config, config_open())
        config_makedirs.assert_called_once_with("/fake")


if __name__ == "__main__":
    unittest.main()
