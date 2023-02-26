
import logging

from xml.dom.minidom import getDOMImplementation

from lisp.core.plugin import PluginNotLoadedError
from lisp.plugins import get_plugin


logger = logging.getLogger(__name__) # pylint: disable=invalid-name

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
        except PluginNotLoadedError:
            return []

        if not midi.is_loaded() or not controller.is_loaded():
            return []

        midi_controls = controller.Config.get('protocols.midi', None)
        if not midi_controls:
            return []

        from lisp.plugins.controller.common import LayoutAction
        from lisp.plugins.midi.midi_utils import midi_str_to_dict

        # Group the commands together by MIDI Channel
        control_definitions = [[] for _ in range(16)]
        for control in midi_controls:
            control_msg = midi_str_to_dict(control[0])
            control_definitions[control_msg['channel']].append([control_msg] + list(control[1:]))

        # Sort by how much each Channel is used
        control_definitions.sort(key=len, reverse=True)

        action_dict = {
            LayoutAction.Go.name: "Go",
            LayoutAction.StopAll.name: "StopAll",
            LayoutAction.InterruptAll.name: "StopAll",
            LayoutAction.StandbyBack.name: "GoBack",
            LayoutAction.StandbyForward.name: "GoNext",
        }
        devices = []
        # Transfer only the two most frequently used Channels
        for definition_set in control_definitions[:2]:
            if not definition_set:
                continue

            device = self._dom.createElement("PRCCDevice")

            # Device Type:
            #   MIDIIn | RS232In
            device.appendChild(
                self.create_text_element("PRCCDevType", "MIDIIn"))

            # MIDIIn Control Method:
            #   Custom | ETC AB | ETC CD | MMC | MSC | ON | Palladium | PC127 | PC128
            #
            #   This appears to be used as a "template" for initial
            #   creation of assignments in the SCS UI, rather than
            #   limiting what can and what can't be sent from this device.
            device.appendChild(
                self.create_text_element("PRCCMidiCtrlMethod", "Custom"))

            # MIDI Channel:
            #   Req. unless PRCCMidiCtrlMethod is MMC | MSC
            #   integer; 1 -> 16
            device.appendChild(
                self.create_text_element("PRCCMidiChannel", definition_set[0][0]['channel'] + 1))

            # Set the commands used by this device
            for command_definition in definition_set:
                command_dict = command_definition[0]
                command_action = command_definition[1]

                if command_action not in action_dict:
                    logger.warn(f"Action {command_action} not aliased.")
                    continue

                if command_dict['type'] == 'program_change':
                    cmd = 0xC
                    cc = command_dict['program']
                    vv = None
                elif command_dict['type'] in ['note_on', 'note_off']:
                    cmd = 0x8 if command_dict['type'] == 'note_on' else 0x9
                    cc = command_dict['note']
                    vv = command_dict['velocity']
                elif command_dict['type'] == 'control_change':
                    cmd = 0xB
                    cc = command_dict['control']
                    vv = command_dict['value']
                else:
                    logger.warn(f"Non-configured command: {command_dict}")
                    continue

                midi_command = self._dom.createElement("PRCCMidiCommand")

                midi_command.appendChild(
                    self.create_text_element("PRCCMidiCmdType", action_dict[command_action]))

                midi_command.appendChild(
                    self.create_text_element("PRCCMidiCmd", cmd))

                midi_command.appendChild(
                    self.create_text_element("PRCCMidiCC", cc))

                if vv is not None:
                    midi_command.appendChild(
                        self.create_text_element("PRCCMidiVV", vv))

                device.appendChild(midi_command)

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
