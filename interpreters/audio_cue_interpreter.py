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
        Pan{x}          integer     0 -> *500 -> 1000

        LvlPtLvlSelA    enum        LvlIndiv | LvlSync | LvlLink
        LvlPtPanSelA    enum        PanUseAudDev | PanIndiv | PanSync

        LvlPt           array       A point of the integrated fade envelope
            LvlPtType                   Start | FadeIn | FadeOut | End
            LvlPtItem       array
                LvlPtItemLogicalDev     string      device name
                LvlPtItemRelDBLevel     float       volume
                LvlPtItemPan            integer     0 -> *500 -> 1000
"""

from lisp.backend.audio_utils import linear_to_db
from lisp.plugins import get_plugin

from ..util import ExportKeys, ScsAudioDevice, ScsDeviceType


class AudioCueInterpreter:

    lisp_plugin = "GstBackend"
    lisp_cuetype = "GstMediaCue"
    scs_cuetype = "F"

    def __init__(self):
        print("Audio cue interpreter init")

    def _build_audio_device(self, exporter, lisp_cue):

        if hasattr(lisp_cue.media.elements, "AutoSink"):
            sink_name = "System"
            sink_channels = 2

        elif hasattr(lisp_cue.media.elements, "AlsaSink"):
            # @todo: Implement AlsaSink handling
            sink_name = "Alsa"
            sink_channels = 2

        elif hasattr(lisp_cue.media.elements, "JackSink"):
            # @todo: Implement JackSink handling
            sink_name = "Jack"
            sink_channels = 8 # @todo: Get actual number

        elif hasattr(lisp_cue.media.elements, "PulseSink"):
            # @todo: Implement PulseSink handling
            sink_name = "Pulse"
            sink_channels = 2

        else:
            print("No Sink?")
            for elem in lisp_cue.media.elements:
                print(elem)
            return ()

        return (
            self._determine_export_cue_type(lisp_cue),
            ScsAudioDevice(
                name=sink_name,
                channels=sink_channels
            )
        )

    def _determine_export_cue_type(self, lisp_cue):
        uri = lisp_cue.media.elements.UriInput.uri
        ext = uri[uri.rindex('.') + 1:]
        exts = get_plugin('GstBackend').supported_extensions()
        if ext in exts['audio']:
            return ScsDeviceType.Audio
        if ext in exts['video']:
            return ScsDeviceType.VideoAudio
        print(f"Unable to determine type of file extension {ext}!")
        return None

    def export_cue(self, exporter, lisp_cue):
        if not hasattr(lisp_cue.media.elements, "UriInput"):
            # @todo: Warn user that this cue will be skipped before export process
            return []

        scs_cue = exporter.build_generic_cue(lisp_cue)
        subcue = exporter.build_generic_subcue(lisp_cue, self.scs_cuetype)
        details = exporter.dom.createElement("AudioFile")

        # @todo:
        # * lose the file:/// prefix
        # * change the slashes from `/` to `\`
        uri = lisp_cue.media.elements.UriInput.uri
        details.appendChild(exporter.create_text_element("FileName", uri))

        # @todo:
        # * Use actual device name
        details.appendChild(exporter.create_text_element("LogicalDev0", "Front"))

        if hasattr(lisp_cue.media.elements, "Volume"):
            details.appendChild(
                exporter.create_text_element(
                    "DBLevel0", linear_to_db(lisp_cue.media.elements.Volume.volume)))

        if hasattr(lisp_cue.media.elements, "AudioPan"):
            # LiSP pan: -1.0 <-> 1.0
            # SCS pan: 0 -> 1000
            details.appendChild(
                exporter.create_text_element(
                    "Pan0", int((lisp_cue.media.elements.AudioPan.pan + 1) * 500)))

        subcue.appendChild(details)
        scs_cue.appendChild(subcue)
        return {
            ExportKeys.Cues: [scs_cue],
            ExportKeys.Device: self._build_audio_device(exporter, lisp_cue),
        }

    def import_cue(self, scs_cue):
        pass
