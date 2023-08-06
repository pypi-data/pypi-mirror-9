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
from itertools import chain
import pkg_resources

from PyQt5 import QtCore, QtGui, QtWidgets, uic

from .core import Plugin, find_plugins, make_command, execute_command


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, config, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(pkg_resources.resource_filename(
            "pyparadox",
            "resources/ui/MainWindow.ui"),
            self)

        self._config = config

        self._modsModel = PluginListModel(self)
        self.modsView.setModel(self._modsModel)
        self._dlcsModel = PluginListModel(self)
        self.dlcsView.setModel(self._dlcsModel)
        self._expansionsModel = PluginListModel(self)
        self.expansionsView.setModel(self._expansionsModel)

        self._resetModels()

        image = QtGui.QPixmap(pkg_resources.resource_filename(
            "pyparadox",
            "resources/{}.png".format(self._config["game"])))
        self.imageLbl.setPixmap(image)

        self.setWindowIcon(QtGui.QIcon(pkg_resources.resource_filename(
                                       "pyparadox", "resources/paradox.png")))

    def _resetModels(self):
        mods = find_plugins(self._config["mod_path"], "mod",
                            config=self._config)
        dlc_path = os.path.join(os.path.dirname(self._config["binary_path"]),
                                "dlc")
        dlc_likes = find_plugins(dlc_path, "dlc", config=self._config)
        dlcs = [dlc for dlc in dlc_likes if dlc.plugin_type == Plugin.DLC]
        expansions = [exp for exp in dlc_likes if exp.plugin_type ==
                      Plugin.EXPANSION]

        self._modsModel.setPluginList(mods)
        self._dlcsModel.setPluginList(dlcs)
        self._expansionsModel.setPluginList(expansions)

    def _savePlugins(self):
        mods = [mod.file_name for mod in self._modsModel if mod.enabled]
        excluded_dlcs = [dlc.file_name for dlc in chain(self._dlcsModel,
                         self._expansionsModel) if not dlc.enabled]

        self._config["mods"] = mods
        self._config["excluded_dlcs"] = excluded_dlcs
        self._config.save()

    @QtCore.pyqtSlot(bool)
    def on_configBtn_clicked(self, pressed):
        configDlg = ConfigDlg(self)
        configDlg.binaryPathEdit.setText(self._config["binary_path"])
        configDlg.modPathEdit.setText(self._config["mod_path"])

        if configDlg.exec_():
            self._config["binary_path"] = configDlg.binaryPathEdit.text()
            self._config["mod_path"] = configDlg.modPathEdit.text()
            self._savePlugins()
            self._resetModels()

    @QtCore.pyqtSlot(bool)
    def on_runBtn_clicked(self, pressed):
        self._savePlugins()

        command = make_command(self._config["binary_path"],
                               self._config["mods"],
                               self._config["excluded_dlcs"])
        try:
            execute_command(command)
        except OSError:
            print("Running {} failed".format(command))
        else:
            self.close()


class ConfigDlg(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(pkg_resources.resource_filename(
            "pyparadox",
            "resources/ui/ConfigDlg.ui"),
            self)

    @QtCore.pyqtSlot(bool)
    def on_binaryPathBtn_clicked(self, pressed):
        old_path = self.binaryPathEdit.text()
        if os.path.isfile(old_path):
            old_dir = os.path.dirname(old_path)
        else:
            old_dir = os.path.expanduser("~")

        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.tr("Choose binary"),
            old_dir)

        if path:
            self.binaryPathEdit.setText(path)

    @QtCore.pyqtSlot(bool)
    def on_modPathBtn_clicked(self, pressed):
        old_path = self.modPathEdit.text()
        if not os.path.isdir(old_path):
            old_path = os.path.expanduser("~")

        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            self.tr("Choose mod folder"),
            old_path)

        if path:
            self.modPathEdit.setText(path)


class PluginListModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super(PluginListModel, self).__init__(parent)
        self._plugins = []

    def __iter__(self):
        return iter(self._plugins)

    def setPluginList(self, plugins):
        self.beginResetModel()
        self._plugins = sorted(plugins, key=lambda x: x.name)
        self.endResetModel()

    def rowCount(self, parent):
        return len(self._plugins)

    def data(self, index, role):
        item = self._plugins[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return item.name
        elif role == QtCore.Qt.CheckStateRole:
            return QtCore.Qt.Checked if item.enabled else QtCore.Qt.Unchecked

    def flags(self, index):
        return (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable |
                QtCore.Qt.ItemIsSelectable)

    def setData(self, index, value, role):
        item = self._plugins[index.row()]
        if role == QtCore.Qt.CheckStateRole:
            item.enabled = bool(value)
        else:
            return False
        return True
