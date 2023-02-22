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


def new_scs_cue(self, lisp_cue):
    """Creates a new SCS cue. Must have at least one SubCue.

    Encapsulating Node: Cue

    Sub Nodes:
        Required:
            CueID               string      e.g. "Q1"
            Description         string
        Optional:
            PageNo              string
            WhenReqd            string      like a second description
            DefDes              bool int    Indicates whether <Description/> is default
            Enabled             bool int
            ActivationMethod    enum        "auto" | <??>
        Seem optional, but may be required if ActivationMethod == "auto":
            AutoActivateCue     string      CueId
            AutoActivatePosn    enum        "start" | <??>
            AutoActivateTime    integer     <milliseconds>
    """
    return {}

def new_scs_subcue(self, lisp_cue):
    """Creates a new SubCue. Each Cue must have at least one SubCue.
    
    Encapsulating Node: Sub
    
    Sub Nodes:
        Required:
            SubType         enum          "M"   (Midi)
                                        | "F"   (Audio)
                                        | "S"   (Fade Out And/Or Stop)
                                        | "L"   (Volume Level Change)
                                        | "K"   (Lighting Control)
        Optional:
            SubDescription  string
            DefSubDes       bool int    Indicates whether <SubDescription/> is default
            RelStartMode    enum        "ae_prev_sub" | "as_cue"
            RelStartTime    integer     <milliseconds>
    """
    return {}
