
from collections import namedtuple
import enum

if not hasattr(enum, 'StrEnum'):
    class StrEnum(enum.Enum):
        @staticmethod
        def _generate_next_value_(name, *_):
            return name.lower()
else:
    from enum import StrEnum

class ExportKeys(StrEnum):
    Cues = enum.auto()
    Device = enum.auto()

class ScsDeviceType(StrEnum):
    Audio = enum.auto()
    Midi = enum.auto()
    VideoAudio = enum.auto()

ScsAudioDevice = namedtuple('ScsAudioDevice', ['name', 'channels'])
ScsMidiDevice = namedtuple('ScsMidiDevice', ['name'])
ScsVideoAudioDevice = namedtuple('ScsVideoAudioDevice', ['name'])

SCS_FILE_EXT = '.scs11'
SCS_FILE_REL_PREFIX = '$(Cue)\\'
SCS_XML_INDENT = ' ' * 4

# SCS supports arbitrary string CueIDs ("Q1", "Q2", "Q3.5", "VID7", ...)
# which stay with cues when moved around a cue list.
#
# LiSP's cue numbers are in fact the index of the cue's position in the
# cue list, and do not stay with cues when moved.
#
# In order to retain the SCS CueID, so users may recognise which cue is
# which as well as for export purposes, we add it to the front of cue names
# when importing, and remove it when exporting.
#
# The following is used as the markup to diffentiate the CueID from the
# rest of the cue name.
#
# It's not perfect, as there's potential issues, such as there being no
# check to make sure CueIDs are unique when exporting.
#
# If/When LiSP also supports arbitrary cue numbers/ids, then this can
# be written out.
CUEID_MARKUP_PREFIX = '[['
CUEID_MARKUP_SUFFIX = ']] '
