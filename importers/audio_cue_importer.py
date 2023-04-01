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

from lisp.backend.audio_utils import db_to_linear

from ._media_import_common import MediaCueImporter


class AudioCueImporter(MediaCueImporter):

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

    def _build_element_volume(self, importer, scs_subcue):
        level = scs_subcue.getElementsByTagName("DBLevel0")
        level = importer.get_float_value(level[0]) if level else -3.0
        return {
            "volume": db_to_linear(level)
        }

    def _get_fadein_time(self, importer, scs_subcue):
        time = scs_subcue.getElementsByTagName("FadeInTime")
        if not time:
            return False
        return importer.get_integer_value(time[0]) / 1000

    def _get_fadeout_time(self, importer, scs_subcue):
        time = scs_subcue.getElementsByTagName("FadeOutTime")
        if not time:
            return False
        return importer.get_integer_value(time[0]) / 1000

    def _get_loop_value(self, importer, scs_subcue):
        looped = scs_subcue.getElementsByTagName("Loop")
        if not looped or not importer.get_integer_value(looped[0]):
            return None
        loop_count = scs_subcue.getElementsByTagName("NumLoops")
        if not loop_count:
            return -1
        return importer.get_integer_value(loop_count[0])
