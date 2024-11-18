
from enum import Enum

from wx.lib.newevent import NewEvent

#
# Constructor returns a tuple; First is the event,  The second is the binder
#
IssuesSelectedEvent,       EVT_ISSUES_SELECTED        = NewEvent()
RepositorySelectedEvent,   EVT_REPOSITORY_SELECTED    = NewEvent()
MilestoneSelectedEvent,    EVT_MILESTONE_SELECTED     = NewEvent()
TaskCreationCompleteEvent, EVT_TASK_CREATION_COMPLETE = NewEvent()


class EventType(Enum):
    """
    """
    IssuesSelected       = 'IssuesSelected'
    RepositorySelected   = 'RepositorySelected'
    MilestoneSelected    = 'MilestoneSelected'
    TaskCreationComplete = 'TaskCreationComplete'
    
