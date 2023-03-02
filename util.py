
from collections import namedtuple
import enum

if not hasattr(enum, 'StrEnum'):
    class StrEnum(enum.Enum):
        @staticmethod
        def _generate_next_value_(name, *_):
            return name.lower()

class ExportKeys(StrEnum):
    Cues = enum.auto()
    Device = enum.auto()

class ScsDeviceType(StrEnum):
    Audio = enum.auto()
    Midi = enum.auto()
    VideoAudio = enum.auto()

ScsAudioDevice = namedtuple('ScsAudioDevice', ['name', 'channels'])
