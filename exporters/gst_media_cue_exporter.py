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

from lisp.backend.audio_utils import linear_to_db
from lisp.plugins import get_plugin

from ..util import ExportKeys, ScsAudioDevice, ScsVideoAudioDevice, ScsDeviceType


class GstMediaCueExporter:

    lisp_plugin = "GstBackend"
    lisp_cuetype = "GstMediaCue"
    scs_subtype_audio = "F"
    scs_subtype_video = "A"

    def __init__(self):
        print("GstMedia cue exporter init")

    def _build_audio_cue(self, exporter, lisp_cue, scs_device, scs_subcue):
        details = exporter.dom.createElement("AudioFile")

        # @todo:
        # * lose the file:/// prefix
        # * change the slashes from `/` to `\`
        uri = lisp_cue.media.elements.UriInput.uri
        details.appendChild(exporter.create_text_element("FileName", uri))

        details.appendChild(exporter.create_text_element("LogicalDev0", scs_device.name))

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

        scs_subcue.appendChild(details)

    def _build_device(self, cue_type, lisp_cue):

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

        if cue_type == ScsDeviceType.Audio:
            return ScsAudioDevice(
                name=sink_name,
                channels=sink_channels
            )
        else:
            return ScsVideoAudioDevice(
                name=sink_name
            )

    def _build_video_cue(self, exporter, lisp_cue, scs_device, scs_subcue):

        scs_subcue.appendChild(
            exporter.create_text_element("OutputScreen", 2))

        scs_subcue.appendChild(
            exporter.create_text_element("VideoLogicalAudioDev", scs_device.name))

        if hasattr(lisp_cue.media.elements, "Volume"):
            scs_subcue.appendChild(
                exporter.create_text_element(
                    "SubDBLevel0", linear_to_db(lisp_cue.media.elements.Volume.volume)))

        if hasattr(lisp_cue.media.elements, "AudioPan"):
            # LiSP pan: -1.0 <-> 1.0
            # SCS pan: 0 -> 1000
            scs_subcue.appendChild(
                exporter.create_text_element("SubDBPan0", int((lisp_cue.media.elements.AudioPan.pan + 1) * 500)))

        video_file = exporter.dom.createElement("VideoFile")

        uri = lisp_cue.media.elements.UriInput.uri
        video_file.appendChild(
            exporter.create_text_element("FileName", uri))

        scs_subcue.appendChild(video_file)

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

        scs_cuetype = self._determine_export_cue_type(lisp_cue)
        scs_device = self._build_device(scs_cuetype, lisp_cue)
        if scs_cuetype == ScsDeviceType.Audio:
            subcue = exporter.build_generic_subcue(lisp_cue, self.scs_subtype_audio)
            self._build_audio_cue(exporter, lisp_cue, scs_device, subcue)

        elif scs_cuetype == ScsDeviceType.VideoAudio:
            subcue = exporter.build_generic_subcue(lisp_cue, self.scs_subtype_video)
            self._build_video_cue(exporter, lisp_cue, scs_device, subcue)

        else:
            return ()

        scs_cue = exporter.build_generic_cue(lisp_cue)
        scs_cue.appendChild(subcue)
        return {
            ExportKeys.Cues: [scs_cue],
            ExportKeys.Device: (
                scs_cuetype,
                scs_device,
            )
        }
