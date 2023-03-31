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

from os import path

from lisp.plugins import get_plugin

from ..util import SCS_FILE_REL_PREFIX


class AudioCueImporter:

    lisp_plugin = "GstBackend"
    lisp_cuetype = "GstMediaCue"
    scs_subtype = "F"

    def __init__(self):
        print("Audio cue importer init")

    def _build_element_uriinput(self, importer, scs_subcue, context):
        file_path = scs_subcue.getElementsByTagName("FileName")[0]
        file_path = importer.get_string_value(file_path)
        file_path = file_path.replace(SCS_FILE_REL_PREFIX, '', 1)
        return {
            "uri": f"file:///{ context['path'] }/{ file_path }",
        }

    def import_cue(self, importer, scs_cue, scs_subcue, context):
        cue_dict = importer.build_generic_cue(scs_cue, scs_subcue)
        media_dict = {}

        elements = {
            "UriInput": self._build_element_uriinput(importer, scs_subcue, context),
        }
        media_dict["elements"] = elements

        pipeline = ["UriInput"] + get_plugin('GstBackend').Config.get("pipeline", [])
        media_dict["pipe"] = pipeline

        cue_dict["media"] = media_dict
        return cue_dict
