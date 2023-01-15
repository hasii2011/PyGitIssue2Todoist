
from typing import Optional

from logging import Logger
from logging import getLogger

from os import sep as osSep

from pkg_resources import resource_filename

from pygitissue2todoist.general.ResourceTextType import ResourceTextType


class Resources:
    """
    Static class
    """
    CANONICAL_APPLICATION_NAME: str = 'PyGitIssue2Todoist'
    RESOURCES_PACKAGE_NAME:     str = 'pygitissue2todoist.resources'
    RESOURCES_PATH:             str = f'pygitissue2todoist{osSep}resources'

    # noinspection SpellCheckingInspection
    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'

    clsLogger: Logger = getLogger(__name__)

    @classmethod
    def retrieveResourceText(cls, textType: ResourceTextType) -> str:
        """
        Look up and retrieve the text associated with the resource type

        Args:
            textType:  The text type from the 'well known' list

        Returns:  A long string
        """
        textFileName: str = Resources.retrieveResourcePath(textType.value)
        cls.clsLogger.debug(f'text filename: {textFileName}')

        objRead = open(textFileName, 'r')
        requestedText: str = objRead.read()
        objRead.close()

        return requestedText

    @classmethod
    def retrieveResourcePath(cls, bareFileName: str) -> str:

        try:
            fqFileName: str = resource_filename(Resources.RESOURCES_PACKAGE_NAME, bareFileName)
        except (ValueError, Exception):
            #
            # Maybe we are in an app
            #
            from os import environ
            pathToResources: Optional[str] = environ.get(f'{Resources.RESOURCE_ENV_VAR}')
            fqFileName = f'{pathToResources}/{Resources.RESOURCES_PATH}/{bareFileName}'

        return fqFileName
