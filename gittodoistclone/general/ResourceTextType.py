
from enum import Enum


class ResourceTextType(Enum):

    SIMPLE_HELP  = 'SimpleHelp.html'
    VERSION_TEXT = 'version.txt'

    def __str__(self):
        return str(self.name)
