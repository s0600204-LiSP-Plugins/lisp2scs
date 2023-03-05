
import logging

from .importers import find_importers


logger = logging.getLogger(__name__) # pylint: disable=invalid-name


class ScsImporter:

    def __init__(self, app):

        self._app = app

        # Find importers (but don't init them)
        self._importers = {}
        for name, importer in find_importers():
            subtype = importer.scs_subtype
            if subtype in self._importers:
                logger.warn(f'Already registered an importer for SCS Cue SubType "{subtype}"')
                continue

            self._importers[subtype] = importer
            logger.debug(f'Registered importer for SCS Cue SubType "{subtype}": {name}.')

    def import_file(self):
        # Obv. can't call it "import" as thats a reserved name.

        # check we have interpreters for the showfile's cues
        print(self._importers)

        # SCS, so:
        # - always list layout
        # - only one list

