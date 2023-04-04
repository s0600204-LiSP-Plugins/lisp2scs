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

try:
    from lisp.plugins.midi.midi_utils import midi_dict_to_str
except ImportError:
    midi_dict_to_str = None


# If None, then it needs to be translated from FREE
MESSAGE_TYPES = {
    "CC": "control_change",
    "FREE": None,
    "MSC": None,
    "OFF": "note_off",
    "ON": "note_on",
    "PC127": "program_change",
    "PC128": "program_change",
}


class ControlCueImporter:

    lisp_plugin = "Midi"
    lisp_cuetype = "MidiCue"
    scs_subtype = "M"

    def __init__(self):
        print("Control cue importer init")

    def import_cue(self, importer, scs_cue, scs_subcue):
        # @todo: Check that this is actually a MIDI message
        #control_type = importer.get_string_value(scs_subcue, "")

        cue_dict = importer.build_generic_cue(scs_cue, scs_subcue)

        for message in scs_subcue.getElementsByTagName("ControlMessage"):
            scs_type = importer.get_string_value(message, "MSMsgType")
            if scs_type not in MESSAGE_TYPES:
                print(f"SCS Midi Message {scs_type} needs support")
                continue

            lisp_midi = {
                "type": MESSAGE_TYPES[scs_type],
            }
            if lisp_midi["type"] is None:
                print(f"SCS Midi Message {scs_type} needs decoding from FREE")
                continue

            if scs_type not in ["FREE", "MSC"]:
                lisp_midi["channel"] = importer.get_integer_value(message, "MSChannel") - 1

            if scs_type == "CC":
                lisp_midi["control"] = importer.get_integer_value(message, "MSParam1")
                lisp_midi["value"] = importer.get_integer_value(message, "MSParam2")
            elif scs_type in ["ON", "OFF"]:
                lisp_midi["note"] = importer.get_integer_value(message, "MSParam1")
                lisp_midi["velocity"] = importer.get_integer_value(message, "MSParam2")
            elif scs_type in ["PC127", "PC128"]:
                lisp_midi["program"] = importer.get_integer_value(message, "MSParam1")
                lisp_midi["program"] -= 1 if scs_type == "PC128" else 0

            message_dict = copy.deepcopy(cue_dict)
            message_dict["message"] = midi_dict_to_str(lisp_midi)
            yield message_dict
