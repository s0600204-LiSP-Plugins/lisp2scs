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

from lisp.backend.audio_utils import db_to_linear
from lisp.plugins import get_plugin

from ..util import SCS_FILE_REL_PREFIX


class MediaCueImporter:

    lisp_plugin = "GstBackend"
    lisp_cuetype = "GstMediaCue"

    def _build_element_pan(self, importer, scs_subcue):
        return {}

    def _build_element_uriinput(self, importer, scs_subcue, context):
        file_path = scs_subcue.getElementsByTagName("FileName")[0]
        file_path = importer.get_string_value(file_path)
        file_path = file_path.replace(SCS_FILE_REL_PREFIX, '', 1)
        return {
            "uri": f"file:///{ context['path'] }/{ file_path }",
        }

    def _build_element_volume(self, importer, scs_subcue):
        return {}

    def _get_fadein_time(self, importer, scs_subcue):
        return 0

    def _get_fadeout_time(self, importer, scs_subcue):
        return 0

    def _get_loop_value(self, *_):
        return None

    def import_cue(self, importer, scs_cue, scs_subcue, context):
        cue_dict = importer.build_generic_cue(scs_cue, scs_subcue)
        media_dict = {}
        elements = {}
        pipeline = []

        # UriInput
        pipeline.append("UriInput")
        elements["UriInput"] = self._build_element_uriinput(importer, scs_subcue, context)

        # Volume
        pipeline.append("Volume")
        elements["Volume"] = self._build_element_volume(importer, scs_subcue)

        # Pan
        pan = self._build_element_pan(importer, scs_subcue)
        if pan:
            pipeline.append("AudioPan")
            elements["AudioPan"] = pan

        # Sink
        pipeline.append(get_plugin('GstBackend').Config.get("pipeline")[-1])

        # Start and Stop times
        start = scs_subcue.getElementsByTagName("StartAt")
        stop = scs_subcue.getElementsByTagName("EndAt")
        if start:
            media_dict["start_time"] = importer.get_integer_value(start[0])
        if stop:
            media_dict["stop_time"] = importer.get_integer_value(stop[0])

        # Loop
        loop = self._get_loop_value(importer, scs_subcue)
        if loop:
            media_dict["loop"] = loop

        # Fade In/Out times
        fade_in = self._get_fadein_time(importer, scs_subcue)
        fade_out = self._get_fadeout_time(importer, scs_subcue)
        if fade_in:
            cue_dict["fadein_duration"] = fade_in
        if fade_out:
            cue_dict["fadeout_duration"] = fade_out

        media_dict["elements"] = elements
        media_dict["pipe"] = pipeline
        cue_dict["media"] = media_dict
        return cue_dict
