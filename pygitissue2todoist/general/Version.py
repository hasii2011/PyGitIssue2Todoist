
from sys import version as pythonVersion

from wx import __version__ as wxVersion

from codeallybasic.SingletonV3 import SingletonV3

from pygitissue2todoist import __version__


class Version(metaclass=SingletonV3):

    __appName__: str = 'PyGitIssue2Todoist'

    __longVersion__: str = "Humberto's Latest Version"
    __website__:     str = 'https://github.com/hasii2011/gittodoistclone/wiki'

    def __init__(self):
        pass

    @property
    def applicationName(self) -> str:
        return Version.__appName__

    @property
    def applicationVersion(self) -> str:
        return __version__

    @property
    def applicationLongVersion(self) -> str:
        return self.__longVersion__

    @property
    def applicationWebSite(self) -> str:
        return self.__website__

    @property
    def pythonVersion(self) -> str:
        return pythonVersion.split(" ")[0]

    @property
    def wxPythonVersion(self) -> str:
        return wxVersion

    @property
    def pyGithubVersion(self) -> str:
        from importlib.metadata import version
        return version('PyGithub')

    @property
    def todoistVersion(self) -> str:
        from importlib.metadata import version

        return version('todoist_api_python')
