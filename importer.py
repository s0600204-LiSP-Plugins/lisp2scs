
import logging
from xml.dom.minidom import parse as xml_parse

from lisp.core.plugin import PluginNotLoadedError
from lisp.plugins import get_plugin

from .importers import find_importers


logger = logging.getLogger(__name__) # pylint: disable=invalid-name


class ScsImporter:

    def __init__(self, app):

        self._app = app

        # Find importers (but don't init them)
        self._importers = {}
        for name, importer in find_importers():
            subtype = importer.scs_subtype
            if subtype in self._importers:
                logger.warn(f'Already registered an importer for SCS Cue SubType "{subtype}"')
                continue

            self._importers[subtype] = importer
            logger.debug(f'Registered importer for SCS Cue SubType "{subtype}": {name}.')

    def get_string_value(self, node):
        return node.childNodes[0].nodeValue

    def import_file(self, file_contents):
        # Obv. can't call it "import" as thats a reserved name.

        # SCS, so:
        # - always list layout
        # - only one list

    def validate_file(self, file_contents):
        checked_types = []
        dom = xml_parse(file_contents)
        validation_passed = True

        for subcue in dom.getElementsByTagName("Sub"):
            subtype = self.get_string_value(subcue.getElementsByTagName("SubType")[0])

            if subtype in checked_types:
                continue
            checked_types.append(subtype)

            # Check we have an importer for this sub cue type
            if subtype not in self._importers:
                logger.warning(f"No registered importer for SCS Sub Cue of type {subtype}")
                validation_passed = False
                continue

            # Check that the plugin the importer requires is installed...
            plugin_name = self._importers[subtype].lisp_plugin
            try:
                plugin = get_plugin(plugin_name)
            except PluginNotLoadedError:
                logger.warning(f'SCS Sub Cue type "{subtype}" requires the {plugin_name} plugin, but this can not be found.')
                validation_passed = False
                continue

            # ...and enabled.
            if not plugin.is_loaded():
                logger.warning(f'SCS Sub Cue type "{subtype}" requires the {plugin_name} plugin, but this is not enabled.')
                validation_passed = False
                continue

        return validation_passed
