
from sys import version as pythonVersion

from wx import __version__ as wxVersion

from importlib.metadata import version


class Version:

    __appName__: str = 'PyGitIssueClone'
    __version__: str = '0.9-Beta'

    __longVersion__: str = "Humberto's Early Beta Version"
    __website__:     str = 'https://github.com/hasii2011/gittodoistclone/wiki'

    @classmethod
    def applicationName(cls) -> str:
        return cls.__appName__

    @classmethod
    def applicationVersion(cls) -> str:
        return cls.__version__

    @classmethod
    def applicationLongVersion(cls) -> str:
        return cls.__longVersion__

    @classmethod
    def applicationWebSite(cls) -> str:
        return cls.__website__

    @classmethod
    def pythonVersion(cls) -> str:
        return pythonVersion.split(" ")[0]

    @classmethod
    def wxPythonVersion(cls) -> str:
        return wxVersion

    @classmethod
    def pyGithubVersion(cls) -> str:
        return version('PyGithub')

    @classmethod
    def todoistVersion(cls) -> str:
        return version('todoist-python')
