
from typing import Dict
from typing import List
from typing import NewType
from typing import TextIO

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from sys import version as pythonVersion

from wx import __version__ as wxVersion

from codeallybasic.SingletonV3 import SingletonV3

from pygitissue2todoist.general.Resources import Resources

from pygitissue2todoist import __version__


PackageName    = NewType('PackageName', str)
PackageVersion = NewType('PackageVersion', str)

PackageVersionsMap = NewType('PackageVersionsMap', Dict[PackageName, PackageVersion])


class Version(metaclass=SingletonV3):

    TODOIST_PACKAGE_NAME: PackageName = PackageName('todoist-api-python')
    GITHUB_PACKAGE_NAME:  PackageName = PackageName('PyGithub')

    # noinspection SpellCheckingInspection
    PACKAGE_VERSIONS_FILENAME: str = 'packageversions.txt'

    __appName__: str = 'PyGitIssue2Todoist'

    __longVersion__: str = "Humberto's Latest Version"
    __website__:     str = 'https://github.com/hasii2011/gittodoistclone/wiki'

    clsLogger: Logger = getLogger(__name__)

    def __init__(self):

        self.logger:       Logger             = Version.clsLogger
        self._pkgVersions: PackageVersionsMap = self._getPackageVersions()

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
        return self._pkgVersions[Version.GITHUB_PACKAGE_NAME]

    @property
    def todoistVersion(self) -> str:
        return self._pkgVersions[Version.TODOIST_PACKAGE_NAME]

    def _getPackageVersions(self) -> PackageVersionsMap:

        packageVersionMap: PackageVersionsMap = PackageVersionsMap({})

        fqFileName: str = Resources.retrieveResourcePath(Version.PACKAGE_VERSIONS_FILENAME)
        self.logger.debug(f'{fqFileName}')

        readDescriptor:     TextIO = open(fqFileName,  mode='r')
        packageNameVersion: str    = readDescriptor.readline()
        while packageNameVersion:

            nameVersion: List[str] = packageNameVersion.split('=')

            pkgName:    PackageName    = PackageName(nameVersion[0])
            pkgVersion: PackageVersion = PackageVersion(nameVersion[1].strip(osLineSep))
            packageVersionMap[pkgName] = pkgVersion

            packageNameVersion = readDescriptor.readline()

        readDescriptor.close()
        return packageVersionMap
