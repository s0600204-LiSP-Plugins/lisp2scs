
import logging
from xml.dom.minidom import parse as xml_parse

from lisp.backend.audio_utils import db_to_linear
from lisp.core.plugin import PluginNotLoadedError
from lisp.plugins import get_plugin

from .importers import find_importers
from .util import SCS_FILE_REL_PREFIX


logger = logging.getLogger(__name__) # pylint: disable=invalid-name


class ScsImporter:

    def __init__(self, app):

        self._app = app
        self._imported_file_path = None

        # Find importers (but don't init them)
        self._importers = {}
        for name, importer in find_importers():
            subtype = importer.scs_subtype
            if subtype in self._importers:
                logger.warn(f'Already registered an importer for SCS Cue SubType "{subtype}"')
                continue

            self._importers[subtype] = importer
            logger.debug(f'Registered importer for SCS Cue SubType "{subtype}": {name}.')

    @property
    def cue_factory(self):
        return self._app.cue_factory

    @property
    def cue_model(self):
        return self._app.cue_model

    def build_generic_cue(self, scs_cue, scs_subcue):
        """Creates a new LiSP cue."""
        cue_dict = {}

        if scs_cue.getElementsByTagName("Sub").length > 1:
            cue_name = scs_subcue.getElementsByTagName("SubDescription")[0]
        else:
            cue_name = scs_cue.getElementsByTagName("Description")[0]

        cue_id = self.get_string_value(scs_cue.getElementsByTagName("CueID")[0])
        cue_name = self.get_string_value(cue_name)
        cue_dict["name"] = f"[{cue_id}] {cue_name}"

        whenreqd = scs_cue.getElementsByTagName("WhenReqd")
        if whenreqd:
            cue_dict["description"] = self.get_string_value(whenreqd[0])

        return cue_dict

    def get_boolean_value(self, node):
        return bool(self.get_string_value(node))

    def get_integer_value(self, node):
        return int(self.get_string_value(node))

    def get_fileuri_value(self, node, tag_name):
        file_path = self.get_string_value(node.getElementsByTagName(tag_name)[0])
        file_path = file_path.replace(SCS_FILE_REL_PREFIX, '', 1)
        return f"file:///{ self._imported_file_path }/{ file_path }"

    def get_float_value(self, node):
        return float(self.get_string_value(node))

    def get_linear_from_db_value(self, node, tag_name):
        decibel = node.getElementsByTagName(tag_name)
        decibel = self.get_float_value(decibel[0]) if decibel else -3.0
        return db_to_linear(decibel)

    def get_pan_value(self, node, tag_name):
        pan = node.getElementsByTagName(tag_name)
        if not pan:
            return 0
        return self.get_integer_value(pan[0]) / 500 - 1

    def get_string_value(self, node):
        return node.childNodes[0].nodeValue

    def get_time_value(self, node, tag_name):
        time = node.getElementsByTagName(tag_name)
        if not time:
            return None
        return self.get_integer_value(time[0]) / 1000

    def import_file(self, file_contents, file_path):
        # Obv. can't call it "import" as thats a reserved name.
        self._imported_file_path = file_path

        dom = xml_parse(file_contents)
        for cue in dom.getElementsByTagName("Cue"):
            for subcue in cue.getElementsByTagName("Sub"):

                subtype = self.get_string_value(subcue.getElementsByTagName("SubType")[0])

                # Initialise an instance of the importer if needed
                if isinstance(self._importers[subtype], type):
                    self._importers[subtype] = self._importers[subtype]()

                cue_dict = self._importers[subtype].import_cue(self, cue, subcue)
                lisp_cue = self._app.cue_factory.create_cue(self._importers[subtype].lisp_cuetype)
                lisp_cue.update_properties(cue_dict)
                self._app.cue_model.add(lisp_cue)

        self._imported_file_path = None

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
