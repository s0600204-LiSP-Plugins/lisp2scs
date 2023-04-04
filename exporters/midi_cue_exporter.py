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

try:
    from lisp.plugins.midi.midi_utils import midi_str_to_dict
except ImportError:
    midi_str_to_dict = None

from ..util import ExportKeys, ScsDeviceType, ScsMidiDevice


# Some messages can be converted directly to SCS equivalents...
MESSAGE_TYPE_MAPPING = {
    "note_on": "ON",
    "note_off": "OFF",
    "control_change": "CC",
    "program_change": "PC127",
}
# ...and others need to be mapped to FREE
MESSAGE_FREE_MAPPING = {
    "polytouch": "A{channel:X} {note:02X} {value:02X}",
    "aftertouch": "D{channel:X} {value:02X}",
    "pitchwheel": "E{channel:X} {pitch:04X}",
    "song_select": "F3 {song:02X}",
    "songpos": "F2 {pos:04X}",
    "start": "FA",
    "stop": "FC",
    "continue": "FB",
}


class MidiCueExporter:

    lisp_plugin = "Midi"
    lisp_cuetype = "MidiCue"
    scs_cuetype = "M"

    def __init__(self):
        print("MIDI cue exporter init")

    def export_cue(self, exporter, lisp_cue):
        scs_device = ScsMidiDevice(name='MIDI')
        scs_cue = exporter.build_generic_cue(lisp_cue)
        subcue = exporter.build_generic_subcue(lisp_cue, self.scs_cuetype)
        details = exporter.dom.createElement("ControlMessage")

        details.appendChild(exporter.create_text_element("CMLogicalDev", scs_device.name))

        message = lisp_cue.properties()['message']
        if message:
            message = midi_str_to_dict(message)

            lisp_type = message['type']
            if lisp_type not in MESSAGE_TYPE_MAPPING and lisp_type not in MESSAGE_FREE_MAPPING:
                print(f"Unrecognized MIDI message type '{ lisp_type }'")
                return None

            scs_type = MESSAGE_TYPE_MAPPING.get(lisp_type, "FREE")
            details.appendChild(exporter.create_text_element("MSMsgType", scs_type))

            if scs_type not in ["MSC", "FREE"]:
                # MSC should be given the device-id here, but mido (and
                # thus LiSP) doesn't support MSC natively.
                details.appendChild(
                    exporter.create_text_element("MSChannel", message['channel'] + 1))

            if scs_type == "CC":
                details.appendChild(exporter.create_text_element("MSParam1", message['control']))
                details.appendChild(exporter.create_text_element("MSParam2", message['value']))
            elif scs_type in ["ON", "OFF"]:
                details.appendChild(exporter.create_text_element("MSParam1", message['note']))
                details.appendChild(exporter.create_text_element("MSParam2", message['velocity']))
            elif scs_type == "PC127":
                details.appendChild(exporter.create_text_element("MSParam1", message['program']))
            else:
                details.appendChild(
                    exporter.create_text_element(
                        "MIDIData",
                        MESSAGE_FREE_MAPPING[lisp_type].format(**message)))

        subcue.appendChild(details)
        scs_cue.appendChild(subcue)
        return {
            ExportKeys.Cues: [scs_cue],
            ExportKeys.Device: (ScsDeviceType.Midi, scs_device)
        }
