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
MESSAGE_TYPE_MAPPING = {
    "CC": "control_change",
    "FREE": None,
    # ~ "MSC": None, # LiSP doesn't support MSC - or raw SYSEX - so this cannot be supported
    "OFF": "note_off",
    "ON": "note_on",
    "PC127": "program_change",
    "PC128": "program_change",
}

MESSAGE_FREE_MAPPING = {
    "A": "polytouch",
    "D": "aftertouch",
    "E": "pitchwheel",
    "F2": "songpos",
    "F3": "song_select",
    "FA": "start",
    "FB": "continue",
    "FC": "stop",
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
            if scs_type not in MESSAGE_TYPE_MAPPING:
                print(f"SCS Midi Message {scs_type} needs support")
                continue

            lisp_midi = {
                "type": MESSAGE_TYPE_MAPPING[scs_type],
            }
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
            else:
                data = importer.get_string_value(message, "MIDIData").replace(" ", "")
                msg_type = data[0:1]
                if msg_type == "F":
                    msg_type = data[0:2]
                else:
                    lisp_midi["channel"] = int(data[1:2], 16)

                if msg_type not in MESSAGE_FREE_MAPPING:
                    print(f"SCS MIDI FREE needs supporting :: {data}")
                    continue

                lisp_midi["type"] = MESSAGE_FREE_MAPPING[msg_type]
                if msg_type == "A":
                    lisp_midi["note"] = int(data[2:4], 16)
                    lisp_midi["value"] = int(data[4:6], 16)
                elif msg_type == "D":
                    lisp_midi["value"] = int(data[2:4], 16)
                elif msg_type == "E":
                    lisp_midi["pitch"] = int(data[2:6], 16)
                elif msg_type == "F2":
                    lisp_midi["pos"] = int(data[2:6], 16)
                elif msg_type == "F3":
                    lisp_midi["song"] = int(data[2:4], 16)

            message_dict = copy.deepcopy(cue_dict)
            message_dict["message"] = midi_dict_to_str(lisp_midi)
            yield message_dict
