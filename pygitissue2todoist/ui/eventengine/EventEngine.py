
from typing import Callable

from logging import Logger
from logging import getLogger

from wx import PostEvent
from wx import Window
from wx import PyEventBinder

from pygitissue2todoist.ui.eventengine.Events import EventType
from pygitissue2todoist.ui.eventengine.Events import IssuesSelectedEvent
from pygitissue2todoist.ui.eventengine.Events import MilestoneSelectedEvent
from pygitissue2todoist.ui.eventengine.Events import RepositorySelectedEvent
from pygitissue2todoist.ui.eventengine.Events import WorkflowSelectedEvent
from pygitissue2todoist.ui.eventengine.IEventEngine import IEventEngine
from pygitissue2todoist.ui.eventengine.Events import TaskCreationCompleteEvent


class EventEngine(IEventEngine):
    """
    The rationale for this class is to isolate the underlying implementation
    of events.  Currently, it depends on the wxPython event loop.  This leaves
    it open to other implementations;

    Get one of these for each Window you want to listen on
    """
    def __init__(self, listeningWindow: Window):

        self._listeningWindow: Window = listeningWindow
        self.logger: Logger = getLogger(__name__)

    def registerListener(self, event: PyEventBinder, callback: Callable):
        self._listeningWindow.Bind(event, callback)

    def sendEvent(self, eventType: EventType, **kwargs):
        """
        Args:
            eventType:
            **kwargs:

        """
        try:
            match eventType:
                case EventType.TaskCreationComplete:
                    self._sendTaskCreationCompleteEvent()
                case EventType.RepositorySelected:
                    self._sendRepositorySelectedEvent()
                case EventType.IssuesSelected:
                    self._sendIssuesSelectedEvent(**kwargs)
                case EventType.MilestoneSelected:
                    self._sendMilestoneSelectedEvent()
                case EventType.WorkflowSelected:
                    self._sendWorkFlowSelectedEvent()
                case _:
                    self.logger.warning(f'Unknown Event Type: {eventType}')
        except KeyError as ke:
            # eMsg: str = f'Invalid keyword parameter. `{ke}`'
            # raise InvalidKeywordException(eMsg)
            self.logger.error(f'Invalid keyword parameter. `{ke}`')

    def _sendRepositorySelectedEvent(self):
        self.logger.info('Sending RepositorySelectedEvent')
        print('Sending RepositorySelectedEvent')
        eventToPost: RepositorySelectedEvent = RepositorySelectedEvent()
        PostEvent(dest=self._listeningWindow, event=eventToPost)

    def _sendWorkFlowSelectedEvent(self):
        self.logger.info('Sending WorkflowSelectedEvent')
        print('Sending WorkflowSelectedEvent')
        eventToPost: WorkflowSelectedEvent = WorkflowSelectedEvent()
        PostEvent(dest=self._listeningWindow, event=eventToPost)

    def _sendIssuesSelectedEvent(self, **kwargs):
        repositoryName: str = kwargs['repositoryName']
        milestoneName:  str = kwargs['milestoneName']
        selectedSimpleGitIssues = kwargs['selectedSimpleGitIssues']
        eventToPost: IssuesSelectedEvent = IssuesSelectedEvent(repositoryName=repositoryName,
                                                               milestoneName=milestoneName,
                                                               selectedSimpleGitIssues=selectedSimpleGitIssues)

        PostEvent(dest=self._listeningWindow, event=eventToPost)

    def _sendMilestoneSelectedEvent(self,):
        eventToPost: MilestoneSelectedEvent = MilestoneSelectedEvent()
        PostEvent(dest=self._listeningWindow, event=eventToPost)

    def _sendTaskCreationCompleteEvent(self):
        eventToPost: TaskCreationCompleteEvent = TaskCreationCompleteEvent()
        PostEvent(dest=self._listeningWindow, event=eventToPost)
