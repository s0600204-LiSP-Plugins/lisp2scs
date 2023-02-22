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

"""SCS MIDI (sub)Cue:

SubCue enum value: "M"
SubCue limit: 16

Encapsulating Node: ControlMessage

Sub Nodes:
    Required:
        CMLogicalDev
        MSMsgType       enum      "FREE"
                                | "PC127"   (Program Change 0-127)
                                | "PC128"   (Program Change 1-128)
                                | "CC"      (Control Change)
                                | "ON"      (Note On)
                                | "OFF"     (Note Off)
                                | "MSC"     (Midi Show Control)

    if MsMsgType == "FREE":
        Required:
            MIDIData    string      <hexcode>

    if MsMsgType == "PC127" || "PC128"
        Required:
            MSChannel   integer     Channel
            MSParam1    integer     Program Number

    if MsMsgType == "CC" || "ON" || "OFF"
        Required:
            MSChannel   integer     Channel
            MSParam1    integer     Control Number
            MSParam2    Integer     Value

    if MsMsgType == "MSC":
        Required:
            MSChannel   string      Device ID
            MSParam1    int enum    Device Type [1=Lighting, 16=Sound, 96=Pyro, ...]
            MSParam2    int enum    [1=Go, 2=Stop, 7=Fire, ...]

    If MsMsgType == "MSC"; MSParam2 == 1 || 2 ("Go", "Stop"):
        Required:
            MSQNumber   string  Cue Number
        Optional:
            MSQList     string
            MSQPath     string

    If MsMsgType == "MSC"; and MSParam2 == 7 ("Fire")
        Required:
            MSMacro     string      Macro Num

"""


class MidiCueInterpreter:

    lisp_plugin = "Midi"
    lisp_cuetype = "MidiCue"
    scs_cuetype = "M"

    def __init__(self):
        pass

    def export_cue(self, lisp_cue):
        pass

    def import_cue(self, scs_cue):
        pass
