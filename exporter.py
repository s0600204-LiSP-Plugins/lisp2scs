
from xml.dom.minidom import getDOMImplementation

from lisp.core.plugin import PluginNotLoadedError
from lisp.plugins import get_plugin


SCS_XML_INDENT = ' ' * 4


class ScsExporter:

    def __init__(self, app):

        self._app = app
        self._impl = getDOMImplementation()
        self._dom = None
        self._prod_id = None

    def export(self, prod_id):
        self._prod_id = prod_id
        self._dom = self._impl.createDocument(None, "Production", None)

        document = self._dom.documentElement

        document.appendChild(self.build_production_head())

        document.appendChild(self._dom.createElement("Files"))

        return self._dom

    def create_text_element(self, element_name, content):
        if isinstance(content, bool):
            content = int(content)

        if isinstance(content, int):
            content = str(content)

        element = self._dom.createElement(element_name)
        element.appendChild(
            self._dom.createTextNode(content))
        return element

    def build_audio_definitions(self):
        """
        .. note: At least one audio device must be defined, even if no audio cues exist.

        .. note: Mappings to actual physical devices are done locally on a machine.
        """

        definitions = []

        # @todo:
        #   Get devices used in cues

        # Devices for playing audio from Audio files
        for idx in range(1):

            # User-definable identifier
            definitions.append(self.create_text_element(f"PRLogicalDev{idx}", "Front"))

            # Device Channel Count
            # @todo: Get channel count of device
            definitions.append(self.create_text_element(f"PRNumChans{idx}", 2))

            # Automatically include device in new audio cues (optional)
            #   Default: False
            # @todo: True only if this is the default ALSA device, or if using Jack
            if not idx:
                definitions.append(self.create_text_element(f"PRAutoIncludeDev{idx}", True))

        # Devices for playing audio from Video files
        for idx in range(1):

            # User-definable identifier
            definitions.append(self.create_text_element(f"PRVidAudLogicalDev{idx}", "Default"))

        # The Audio Device used when Previewing an Audio File
        definitions.append(self.create_text_element("PreviewDevice", "Front"))

        return definitions

    def build_control_rx_definitions(self):
        """
        SCS supports being remotely controlled by either MIDI or RS232.
        LiSP supports MIDI or OSC.

        SCS supports up to two Devices (and there should be a definition
        for each); LiSP only one. Hoever, each SCS MIDI "device" is
        locked to a single MIDI channel, whilst LiSP allows full use of
        all channels on a device.
        """

        try:
            midi = get_plugin("Midi")
            controller = get_plugin("Controller")
            if not midi.is_loaded() or not controller.is_loaded():
                return []
        except PluginNotLoadedError:
            return []

        # @todo:
        #   Iterate through defined controls via MIDI, and group by channel numbers

        devices = []

        device = self._dom.createElement("PRCCDevice")

        # Device Type:
        #   MIDIIn | RS232In
        device.appendChild(
            self.create_text_element("PRCCDevType", "MIDIIn"))

        # MIDIIn Control Method:
        #   Custom | ETC AB | ETC CD | MMC | MSC | ON | Palladium | PC127 | PC128 |
        device.appendChild(
            self.create_text_element("PRCCMidiCtrlMethod", "Custom"))

        # MIDI Channel:
        #   Req. unless Method is MMC | MSC
        device.appendChild(
            self.create_text_element("PRCCMidiChannel", 1)) # integer; 1 -> 16

        # @todo:
        #   Define the commands used
        # ~ <PRCCDevice>
            # ~ <PRCCDevType>MIDIIn</PRCCDevType>
            # ~ <PRCCMidiCtrlMethod>PC127</PRCCMidiCtrlMethod>
            # ~ <PRCCMidiChannel>1</PRCCMidiChannel>
            # ~ <PRCCMidiCommand>
                # ~ <PRCCMidiCmdType>Go</PRCCMidiCmdType>
                # ~ <PRCCMidiCmd>12</PRCCMidiCmd>
                # ~ <PRCCMidiCC>0</PRCCMidiCC>
                # ~ <PRCCMidiVV>0</PRCCMidiVV>
            # ~ </PRCCMidiCommand>
            # ~ <PRCCMidiCommand>
                # ~ <PRCCMidiCmdType>StopAll</PRCCMidiCmdType>
                # ~ <PRCCMidiCmd>12</PRCCMidiCmd>
                # ~ <PRCCMidiCC>1</PRCCMidiCC>
                # ~ <PRCCMidiVV>0</PRCCMidiVV>
            # ~ </PRCCMidiCommand>
            # ~ <PRCCMidiCommand>
                # ~ <PRCCMidiCmdType>GoBack</PRCCMidiCmdType>
                # ~ <PRCCMidiCmd>12</PRCCMidiCmd>
                # ~ <PRCCMidiCC>2</PRCCMidiCC>
                # ~ <PRCCMidiVV>0</PRCCMidiVV>
            # ~ </PRCCMidiCommand>
            # ~ <PRCCMidiCommand>
                # ~ <PRCCMidiCmdType>GoNext</PRCCMidiCmdType>
                # ~ <PRCCMidiCmd>12</PRCCMidiCmd>
                # ~ <PRCCMidiCC>3</PRCCMidiCC>
                # ~ <PRCCMidiVV>0</PRCCMidiVV>
            # ~ </PRCCMidiCommand>
        # ~ </PRCCDevice>

        devices.append(device)

        return devices

    def build_control_tx_definitions(self):
        """
        SCS supports being sending either MIDI or RS232. LiSP supports
        MIDI or OSC.

        LiSP (currently) supports only one MIDI output; the quantity SCS
        supports depends on the version:

        * "Demo"        : 1
        * "Lite"        : 0
        * "Standard"    : 0
        * "Professional": 4
        * "Pro Plus"    : 8
        * "Platinum"    : 16
        """
        try:
            midi = get_plugin("Midi")
            if not midi.is_loaded():
                return []
        except PluginNotLoadedError:
            return []

        # @todo: Determine if there's any MIDI cues, and if there are not, skip this.

        device = self._dom.createElement("PRCSDevice")

        # User-definable identifier for the device
        device.appendChild(
            self.create_text_element("PRCSLogicalDev", "MIDI"))

        # Device Type
        #   MIDIOut | RS232Out
        device.appendChild(
            self.create_text_element("PRCSDevType", "MIDIOut"))

        return [device]

    def build_production_head(self):
        head = self._dom.createElement("Head")

        # Name of the Production
        head.appendChild(self.create_text_element("Title", self._app.session.name()))

        # Unique ID of the SCS Production
        if self._prod_id:
            head.appendChild(self.create_text_element("ProdId", self._prod_id))

        for element in self.build_audio_definitions():
            head.appendChild(element)

        for element in self.build_control_tx_definitions():
            head.appendChild(element)

        for element in self.build_control_rx_definitions():
            head.appendChild(element)

        return head
