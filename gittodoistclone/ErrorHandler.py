
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from os import getenv
from os import path as osPath

from shutil import rmtree

from wx import ICON_INFORMATION
from wx import ICON_QUESTION
from wx import ID_YES
from wx import NO
from wx import NO_DEFAULT
from wx import OK
from wx import YES

from wx import MessageDialog

from gittodoistclone.general.Preferences import Preferences

INVALID_TEMP_ID: int = 16
MAX_PROJECTS:    int = 50

HandledErrors = NewType('HandledErrors', List[int])


class ErrorHandler:

    TODOIST_CACHE_DIRECTORY_NAME: str = '.todoist-sync'

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._preferences: Preferences = Preferences()

        self._errorsHandled: HandledErrors = HandledErrors([INVALID_TEMP_ID])

    def isErrorHandled(self, errorCode: int) -> bool:
        """
        Determine if we can handle this type of error.  Currently only applies to
        the Todoist API

        Args:
            errorCode: Error code to check

        Returns: `True` if we do else `False`

        """

        ans: bool = False

        if errorCode in self._errorsHandled:
            ans = True

        return ans

    def handleError(self, errorMessage: str, errorCode: int):
        """
        Assumes caller has validated we can handle

        Args:
            errorMessage:
            errorCode:
        """

        assert errorCode in self._errorsHandled, 'Developer made  boo boo'

        if self._preferences.cleanTodoistCache is False:
            self._informUserOfOptions(errorMessage)
        else:
            self._doRemedialAction()

    def _doRemedialAction(self):

        msg: str = (
            f'You opted to allow us to clean up certain types of errors by '
            f'removing the Todoist cache. '
            f'I am just double confirming you want to do this?'
        )
        msgDlg: MessageDialog = MessageDialog(parent=None,
                                              message=msg,
                                              caption='Question',
                                              style=YES | NO | NO_DEFAULT | ICON_QUESTION)

        answer: int = msgDlg.ShowModal()
        msgDlg.Destroy()
        if answer == ID_YES:
            self.__removeTodoistCache()

    def _informUserOfOptions(self, errorMessage):
        msg: str = (
            f'Error: "{errorMessage}"   '
            f'This error can usually be handled by deleting the '
            f'Todoist cache.  However, you have that preference turned off '
            f'Turn the preference on and retry your operation'
        )
        msgDlg: MessageDialog = MessageDialog(parent=None,
                                              message=msg,
                                              caption='Information',
                                              style=OK | ICON_INFORMATION)
        msgDlg.ShowModal()
        msgDlg.Destroy()

    def __removeTodoistCache(self):

        homeDir: str = getenv('HOME')   # type: ignore

        directoryToDelete: str = osPath.join(homeDir, ErrorHandler.TODOIST_CACHE_DIRECTORY_NAME)

        rmtree(directoryToDelete)

        msgDlg: MessageDialog = MessageDialog(parent=None,
                                              message='Now quit and restart PyGitIssue2Todoist',
                                              caption='Restart',
                                              style=OK | ICON_INFORMATION)

        msgDlg.ShowModal()
        msgDlg.Destroy()
