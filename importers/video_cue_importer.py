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


class VideoCueImporter(MediaCueImporter):

    scs_subtype = "A"

    def __init__(self):
        print("Video cue importer init")

    def _build_element_pan(self, importer, scs_subcue):
        return {
            "pan": importer.get_pan_value(scs_subcue, "SubDBPan0")
        }

    def _build_element_volume(self, importer, scs_subcue):
        return {
            "volume": importer.get_linear_from_db_value(scs_subcue, "SubDBLevel0")
        }

    def _get_fadein_time(self, importer, scs_subcue):
        time = importer.get_time_value(scs_subcue, "PLFadeInTime")
        return time if time else None

    def _get_fadeout_time(self, importer, scs_subcue):
        time = importer.get_time_value(scs_subcue, "PLFadeOutTime")
        return time if time else None

    def _get_loop_value(self, importer, scs_subcue):
        looped = scs_subcue.getElementsByTagName("VideoRepeat")
        if looped and importer.get_integer_value(looped[0]) == 1:
            return -1
        return 0
