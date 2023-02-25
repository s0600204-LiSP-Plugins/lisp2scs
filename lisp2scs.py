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

from PyQt5.QtWidgets import (
    QAction,
    QMenu,
)

# pylint: disable=import-error
from lisp.core.plugin import Plugin
from lisp.ui.ui_utils import translate

from .exporter import SCS_XML_INDENT, ScsExporter
from .interpreters import find_interpreters


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

        # Find interpreters (but don't init them)
        self._interpreters = {}
        for name, interpreter in find_interpreters():
            cuetype = interpreter.lisp_cuetype
            if cuetype in self._interpreters:
                logger.warn(f"Already registered interpreter for cue type {cuetype}")
                continue

            logger.debug(f"Registering interpreter for {cuetype}: {name}.")
            self._interpreters[cuetype] = interpreter

        # Append actions to File menu
        file_menu = self.app.window.menuFile

        self.import_menu = QMenu(file_menu)
        self.import_action = QAction(self.import_menu)
        self.import_action.triggered.connect(self.import_showfile)
        self.import_menu.addAction(self.import_action)
        self.import_menu.setEnabled(False)

        self.export_menu = QMenu(file_menu)
        self.export_action = QAction(self.export_menu)
        self.export_action.triggered.connect(self.export_showfile)
        self.export_menu.addAction(self.export_action)

        file_menu.insertMenu(self.app.window.editPreferences, self.import_menu)
        file_menu.insertMenu(self.app.window.editPreferences, self.export_menu)
        file_menu.insertSeparator(self.app.window.editPreferences)

        self.retranslateUi()

    def retranslateUi(self):
        self.export_menu.setTitle(translate("Lisp2Scs", "Export"))
        self.export_action.setText(translate("Lisp2Scs", "Show Cue Systems"))

        self.import_menu.setTitle(translate("Lisp2Scs", "Import"))
        self.import_action.setText(translate("Lisp2Scs", "Show Cue Systems"))

    def export_showfile(self):
        # Get used cue types
        cuetypes = {cue.__class__.__name__ for cue in self.app.layout.cues()}

        for cuetype in cuetypes:
            # Check we have an interpreters for each cue type
            if cuetype not in self._interpreters:
                logger.warning(f"No registered interpreter for Cues of type {cuetype}")
                continue

            # And if we do, initialise an instance of it, if needed
            if isinstance(self._interpreters[cuetype], type):
                self._interpreters[cuetype] = self._interpreters[cuetype]()

        # run interpreters
        # prompt for location
        # write file

        exporter = ScsExporter(self.app, self._interpreters)
        document = exporter.export(self._prod_id, self.app.layout.cues())
        print(document.toprettyxml(indent=SCS_XML_INDENT)) # @todo: add `encoding="UTF-8"`

    def import_showfile(self):
        pass
        # check we have interpreters for the showfile's cues
        # SCS, so:
        # - always list layout
        # - only one list
