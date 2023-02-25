
from xml.dom.minidom import getDOMImplementation

from lisp.core.plugin import PluginNotLoadedError
from lisp.plugins import get_plugin


SCS_XML_INDENT = ' ' * 4


class ScsExporter:

    def __init__(self, app, interpreters):

        self._app = app
        self._impl = getDOMImplementation()
        self._dom = None
        self._prod_id = None
        self._interpreters = interpreters

    @property
    def dom(self):
        return self._dom

    def export(self, prod_id, cues):
        self._prod_id = prod_id
        self._dom = self._impl.createDocument(None, "Production", None)

        document = self._dom.documentElement

        document.appendChild(self.build_production_head())

        for lisp_cue in cues:
            cue_type = lisp_cue.__class__.__name__
            if cue_type not in self._interpreters:
                # A warning has already been given if no appropriate interpreter is present
                continue

            for scs_cue in self._interpreters[cue_type].export_cue(self, lisp_cue):
                document.appendChild(scs_cue)

        return self._dom

    def create_text_element(self, element_name, content):
        if isinstance(content, bool):
            content = int(content)

        if isinstance(content, int) or isinstance(content, float):
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

    def build_generic_cue(self, lisp_cue):
        """Creates a new SCS cue. Must have at least one SubCue.

        Encapsulating Node: Cue

        Sub Nodes:
            Required:
                CueID               string      e.g. "Q1"
                Description         string      Used in the SCS UI as a Cue Name
            Optional:
                PageNo              string
                WhenReqd            string
                DefDes              bool int    Indicates whether <Description/> is default
                Enabled             bool int
                ActivationMethod    enum        "auto" | <??>
            Seem optional, but may be required if ActivationMethod == "auto":
                AutoActivateCue     string      CueId
                AutoActivatePosn    enum        "start" | <??>
                AutoActivateTime    integer     <milliseconds>
        """
        scs_cue = self._dom.createElement("Cue")
        scs_cue.appendChild(self.create_text_element("CueID", lisp_cue.index + 1))
        scs_cue.appendChild(self.create_text_element("Description", lisp_cue.name))
        if lisp_cue.description:
            scs_cue.appendChild(self.create_text_element("WhenReqd", lisp_cue.description))
        return scs_cue

    def build_generic_subcue(self, lisp_cue, scs_cuetype):
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
                SubDescription  string      Used in the SCS UI as SubCue Name
                DefSubDes       bool int    Indicates whether <SubDescription/> is default
                RelStartMode    enum        "ae_prev_sub" | "as_cue" | "as_prev_sub"
                RelStartTime    integer     <milliseconds>
        """
        scs_subcue = self._dom.createElement("Sub")
        scs_subcue.appendChild(self.create_text_element("SubType", scs_cuetype))
        scs_subcue.appendChild(self.create_text_element("SubDescription", lisp_cue.name))
        return scs_subcue

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
