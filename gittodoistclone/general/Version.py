
from typing import Dict
from typing import List
from typing import NewType
from typing import TextIO

from logging import Logger
from logging import getLogger

from os import sep as osSep
from os import linesep as osLineSep

from sys import version as pythonVersion

from pkg_resources import resource_filename

from wx import __version__ as wxVersion

from gittodoistclone.general.Singleton import Singleton

PackageName    = NewType('PackageName', str)
PackageVersion = NewType('PackageVersion', str)

PackageVersionsMap = NewType('PackageVersionsMap', Dict[PackageName, PackageVersion])


class Version(Singleton):

    RESOURCES_PACKAGE_NAME: str = 'gittodoistclone.resources'
    RESOURCES_PATH:         str = f'gittodoistclone{osSep}resources'

    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'

    PACKAGE_VERSIONS_FILENAME: str = 'packageversions.txt'

    __appName__: str = 'PyGitIssueClone'
    __version__: str = '0.9-Beta'

    __longVersion__: str = "Humberto's Beta Version"
    __website__:     str = 'https://github.com/hasii2011/gittodoistclone/wiki'

    clsLogger: Logger = getLogger(__name__)

    def init(self):

        self.logger:       Logger             = Version.clsLogger
        self._pkgVersions: PackageVersionsMap = self._getPackageVersions()

    @property
    def applicationName(self) -> str:
        return Version.__appName__

    @property
    def applicationVersion(self) -> str:
        return Version.retrieveResourceText('version.txt')

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
        return self._pkgVersions['PyGithub']

    @property
    def todoistVersion(self) -> str:
        return self._pkgVersions['todoist-python']

    @classmethod
    def retrieveResourceText(cls, bareFileName: str) -> str:
        """
        Get text out of file

        Args:
            bareFileName:

        Returns:  A long string
        """
        textFileName: str = Version.retrieveResourcePath(bareFileName)
        cls.clsLogger.debug(f'{textFileName=}')

        objRead = open(textFileName, 'r')
        requestedText: str = objRead.read()
        objRead.close()

        return requestedText

    @classmethod
    def retrieveResourcePath(cls, bareFileName: str) -> str:

        # Use this method in Python 3.9
        # from importlib_resources import files
        # configFilePath: str  = files('gittodoistclone.resources').joinpath('bareFileName')

        try:
            fqFileName: str = resource_filename(Version.RESOURCES_PACKAGE_NAME, bareFileName)
        except (ValueError, Exception):
            #
            # Maybe we are in an app
            #
            from os import environ
            pathToResources: str = environ.get(f'{Version.RESOURCE_ENV_VAR}')
            fqFileName:      str = f'{pathToResources}{osSep}{Version.RESOURCES_PATH}{osSep}{bareFileName}'

        return fqFileName

    def _getPackageVersions(self) -> PackageVersionsMap:

        packageVersionMap: PackageVersionsMap = PackageVersionsMap({})

        fqFileName: str = Version.retrieveResourcePath(Version.PACKAGE_VERSIONS_FILENAME)
        self.logger.debug(f'{fqFileName}')

        readDescriptor:     TextIO = open(fqFileName,  mode='r')
        packageNameVersion: str    = readDescriptor.readline()
        while packageNameVersion:

            nameVersion: List[str] = packageNameVersion.split('=')

            packageVersionMap[nameVersion[0]] = nameVersion[1].strip(osLineSep)

            packageNameVersion = readDescriptor.readline()

        return packageVersionMap
