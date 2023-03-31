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


class AudioCueImporter:

    lisp_plugin = "GstBackend"
    lisp_cuetype = "GstMediaCue"
    scs_subtype = "F"

    def __init__(self):
        print("Audio cue importer init")

    def _build_element_pan(self, importer, scs_subcue):
        pan = scs_subcue.getElementsByTagName("Pan0")
        if not pan:
            return None
        return {
            "pan": importer.get_integer_value(pan[0]) / 500 - 1
        }

    def _build_element_uriinput(self, importer, scs_subcue, context):
        file_path = scs_subcue.getElementsByTagName("FileName")[0]
        file_path = importer.get_string_value(file_path)
        file_path = file_path.replace(SCS_FILE_REL_PREFIX, '', 1)
        return {
            "uri": f"file:///{ context['path'] }/{ file_path }",
        }

    def _build_element_volume(self, importer, scs_subcue):
        level = scs_subcue.getElementsByTagName("DBLevel0")
        level = importer.get_float_value(level[0]) if level else -3.0
        return {
            "volume": db_to_linear(level)
        }

    def _build_loop_value(self, importer, scs_subcue):
        looped = scs_subcue.getElementsByTagName("Loop")
        if not looped or not importer.get_integer_value(looped[0]):
            return None
        loop_count = scs_subcue.getElementsByTagName("NumLoops")
        if not loop_count:
            return -1
        return importer.get_integer_value(loop_count[0])

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
        loop = self._build_loop_value(importer, scs_subcue)
        if loop:
            media_dict["loop"] = loop

        # Fade In/Out times
        fade_in = scs_subcue.getElementsByTagName("FadeInTime")
        fade_out = scs_subcue.getElementsByTagName("FadeOutTime")
        if fade_in:
            cue_dict["fadein_duration"] = importer.get_integer_value(fade_in[0]) / 1000
        if fade_out:
            cue_dict["fadeout_duration"] = importer.get_integer_value(fade_out[0]) / 1000

        media_dict["elements"] = elements
        media_dict["pipe"] = pipeline
        cue_dict["media"] = media_dict
        return cue_dict
