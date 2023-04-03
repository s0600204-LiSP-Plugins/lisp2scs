
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
            cue_name = self.get_string_value(scs_subcue, "SubDescription")
        else:
            cue_name = self.get_string_value(scs_cue, "Description")

        cue_id = self.get_string_value(scs_cue, "CueID")
        cue_dict["name"] = f"[{cue_id}] {cue_name}"

        whenreqd = self.get_string_value(scs_cue, "WhenReqd")
        if whenreqd:
            cue_dict["description"] = whenreqd

        return cue_dict

    def get_boolean_value(self, node, tag_name):
        value = self.get_string_value(node, tag_name)
        if value is None:
            return None
        return bool(node)

    def get_integer_value(self, node, tag_name):
        value = self.get_string_value(node, tag_name)
        if value is None:
            return None
        return int(value)

    def get_fileuri_value(self, node, tag_name):
        file_path = self.get_string_value(node, tag_name)
        if file_path is None:
            return None
        file_path = file_path.replace(SCS_FILE_REL_PREFIX, '', 1)
        return f"file:///{ self._imported_file_path }/{ file_path }"

    def get_float_value(self, node, tag_name):
        value = self.get_string_value(node, tag_name)
        if value is None:
            return None
        return float(value)

    def get_linear_from_db_value(self, node, tag_name):
        decibel = self.get_float_value(node, tag_name)
        return db_to_linear(-3.0 if decibel is None else decibel)

    def get_pan_value(self, node, tag_name):
        pan = self.get_integer_value(node, tag_name)
        if pan is None:
            return 0
        return pan / 500 - 1

    def get_string_value(self, node, tag_name):
        elems = node.getElementsByTagName(tag_name)
        return elems[0].childNodes[0].nodeValue if elems else None

    def get_time_value(self, node, tag_name):
        time = self.get_integer_value(node, tag_name)
        if time is None:
            return None
        return time / 1000

    def import_file(self, file_contents, file_path):
        # Obv. can't call it "import" as thats a reserved name.
        self._imported_file_path = file_path

        dom = xml_parse(file_contents)
        for cue in dom.getElementsByTagName("Cue"):
            for subcue in cue.getElementsByTagName("Sub"):

                subtype = self.get_string_value(subcue, "SubType")

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
            subtype = self.get_string_value(subcue, "SubType")

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
