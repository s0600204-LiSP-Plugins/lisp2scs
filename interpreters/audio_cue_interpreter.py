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

"""SCS Audio (sub)Cue:

SubCue enum value: "F"

Encapsulating Node: AudioFile

Sub Nodes:
    Required:
        FileName - string; relational path to file

    Optional:
        FadeInTime      integer     <milliseconds>
        FadeOutTime     integer     <milliseconds>
        StartAt         integer     <milliseconds>
        EndAt           integer     <milliseconds>
        Loop            integer
        LoopStart       integer     <milliseconds>
        LoopEnd         integer     <milliseconds>

        LogicalDev{x}   string      device name
        DBLevel{x}      float       volume

    Optional in 11.2.3:
        Pan{x}          integer

    Optional in 11.4.0.3 and 11.4.1.1:
        ## The following exists on every AudioFile subcue @ 11.4.0.3, 11.4.1.1, but not @ 11.2.3
        LvlPtLvlSelA    ??          ["LvlIndiv"]
        LvlPtPanSelA    ??          ["PanUseAudDev"]
        LvlPt           array
            LvlPtType                   ["FadeIn", "End"]
            LvlPtItem       array
                LvlPtItemLogicalDev     string      device name
                LvlPtItemRelDBLevel     float       volume
"""


class AudioCueInterpreter:

    lisp_plugin = "GstBackend"
    lisp_cuetype = "GstMediaCue"
    scs_cuetype = "F"

    def __init__(self):
        pass

    def export_cue(self, lisp_cue):
        pass

    def import_cue(self, scs_cue):
        pass
