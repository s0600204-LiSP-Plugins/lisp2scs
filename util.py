
import enum

if not hasattr(enum, 'StrEnum'):
    class StrEnum(enum.Enum):
        @staticmethod
        def _generate_next_value_(name, *_):
            return name.lower()

class ExportKeys(StrEnum):
    Cues = enum.auto()
