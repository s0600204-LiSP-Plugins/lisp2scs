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

import copy


class PlaylistCueImporter:

    lisp_plugin = "GstBackend"
    lisp_cuetype = "GstMediaCue"
    scs_subtype = "P"

    def __init__(self):
        print("Playlist cue importer init")

    def import_cue(self, importer, scs_cue, scs_subcue):
        master_level = importer.get_linear_from_db_value(scs_subcue, "PLMastDBLevel0")
        cue_dict = importer.build_generic_cue(scs_cue, scs_subcue)

        for entry in scs_subcue.getElementsByTagName("Sub"):
            entry_dict = copy.deepcopy(cue_dict)
            elements = {}
            pipeline = []

            # UriInput
            pipeline.append("UriInput")
            elements["UriInput"] = {
                "uri": importer.get_fileuri_value(entry, "FileName")
            }

            # Volume
            #   We assume that PLRelLevel is always set.
            pipeline.append("Volume")
            rel_level = importer.get_integer_value(entry, "PLRelLevel") / 100
            elements["Volume"] = {
                "volume": master_level * rel_level
            }

            # Pan
            pipeline.append("AudioPan")
            elements["AudioPan"] = 0

            # Sink
            pipeline.append(get_plugin('GstBackend').Config.get("pipeline")[-1])

            entry_dict["media"] = {
                "elements": elements,
                "pipe": pipeline,
            }
            yield entry_dict
