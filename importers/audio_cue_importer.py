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

from ._media_import_common import MediaCueImporter


class AudioCueImporter(MediaCueImporter):

    scs_subtype = "F"

    def __init__(self):
        print("Audio cue importer init")

    def _build_element_pan(self, importer, scs_subcue):
        return {
            "pan": importer.get_pan_value(scs_subcue, "Pan0")
        }

    def _build_element_volume(self, importer, scs_subcue):
        return {
            "volume": importer.get_linear_from_db_value(scs_subcue, "DBLevel0")
        }

    def _get_fadein_time(self, importer, scs_subcue):
        time = importer.get_time_value(scs_subcue, "FadeInTime")
        return time if time else None

    def _get_fadeout_time(self, importer, scs_subcue):
        time = importer.get_time_value(scs_subcue, "FadeOutTime")
        return time if time else None

    def _get_loop_value(self, importer, scs_subcue):
        looped = importer.get_boolean_value(scs_subcue, "Loop")
        if not looped:
            return None
        loop_count = importer.get_integer_value(scs_subcue, "NumLoops")
        return -1 if loop_count is None else loop_count
