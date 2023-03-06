# This file is a derivation of work on - and as such shares the same
# licence as - Linux Show Player
#
# Linux Show Player:
#   Copyright 2012-2023 Francesco Ceruti <ceppofrancy@gmail.com>
#
# This file:
#   Copyright 2023 s0600204
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os

from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QMenu,
)

# pylint: disable=import-error
from lisp.core.plugin import Plugin
from lisp.ui.ui_utils import translate

from .exporter import ScsExporter
from .importer import ScsImporter
from .util import SCS_FILE_EXT, SCS_XML_INDENT


logger = logging.getLogger(__name__) # pylint: disable=invalid-name


class Lisp2Scs(Plugin):
    """Provides ability to export to a Show Cue Systems compatible showfile."""

    Name = 'Export to SCS'
    Authors = ('s0600204',)
    Depends = ()
    Description = 'Provides ability to export to a Show Cue Systems compatible showfile.'

    def __init__(self, app):
        super().__init__(app)

        # Device Maps (which sound/video/lighting interfaces are in use)
        # are stored locally on a show machine, rather than being saved
        # to a showfile. The ProdId identifies which Device Map to use.
        #
        # We don't create one - we don't know the rules - but we can
        # save an existing one on Import.
        #
        # @todo: Null this on LiSP showfile creation(/loading)
        self._prod_id = None

        self._exporter = None
        self._importer = None

        # Append actions to File menu
        file_menu = self.app.window.menuFile

        self.import_menu = QMenu(file_menu)
        self.import_action = QAction(self.import_menu)
        self.import_action.triggered.connect(self.import_showfile)
        self.import_menu.addAction(self.import_action)

        self.export_menu = QMenu(file_menu)
        self.export_action = QAction(self.export_menu)
        self.export_action.triggered.connect(self.export_showfile)
        self.export_menu.addAction(self.export_action)

        file_menu.insertMenu(self.app.window.editPreferences, self.import_menu)
        file_menu.insertMenu(self.app.window.editPreferences, self.export_menu)
        file_menu.insertSeparator(self.app.window.editPreferences)

        self.retranslateUi()

    def _fileio_startpoint(self):
        if self.app.session.session_file:
            return self.app.session.dir()
        return self.app.conf.get("session.lastPath", os.getenv("HOME"))

    def retranslateUi(self):
        self.export_menu.setTitle(translate("Lisp2Scs", "Export"))
        self.export_action.setText(translate("Lisp2Scs", "Show Cue Systems"))

        self.import_menu.setTitle(translate("Lisp2Scs", "Import"))
        self.import_action.setText(translate("Lisp2Scs", "Show Cue Systems"))

    def export_showfile(self):
        filename = self.get_export_filename()
        if not filename:
            return

        if not self._exporter:
            self._exporter = ScsExporter(self.app)

        document = self._exporter.export(self._prod_id, self.app.layout.cues())

        with open(filename, mode="w", encoding="utf-8") as file:
            file.write(document.toprettyxml(indent=SCS_XML_INDENT))

    def get_export_filename(self):
        path, _ = QFileDialog.getSaveFileName(
            parent=self.app.window,
            filter=f"*{SCS_FILE_EXT}",
            directory=self._fileio_startpoint()
        )

        if path:
            if not path.endswith(SCS_FILE_EXT):
                path += SCS_FILE_EXT
            return path
        return None

    def get_import_filename(self):
        path, _ = QFileDialog.getOpenFileName(
            parent=self.app.window,
            filter=f"*{SCS_FILE_EXT}",
            directory=self._fileio_startpoint()
        )

        if path:
            if not path.endswith(SCS_FILE_EXT):
                path += SCS_FILE_EXT
            return path
        return None

    def import_showfile(self):
        print(self.get_import_filename())

        if not self._importer:
            self._importer = ScsImporter(self.app)

        self._importer.import_file()
