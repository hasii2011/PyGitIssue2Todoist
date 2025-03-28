
from typing import Dict
from typing import List
from typing import NewType

from dataclasses import dataclass
from dataclasses import field

from todoist_api_python.models import Project
from todoist_api_python.models import Task


@dataclass
class GitIssueInfo:
    slug:         str = ''
    gitIssueName: str = ''
    gitIssueURL:  str = ''
    labels:       List[str] = field(default_factory=list)


@dataclass
class CloneInformation:
    repositoryTask:    str = ''
    milestoneNameTask: str = ''
    tasksToClone:      List[GitIssueInfo] = field(default_factory=list)


Tasks             = NewType('Tasks', List[Task])
ProjectName       = NewType('ProjectName', str)
ProjectDictionary = NewType('ProjectDictionary', Dict[ProjectName, Project])


def tasksFactory() -> Tasks:
    return Tasks([])


TaskName     = NewType('TaskName',     str)
TaskId       = NewType('TaskId',       str)
TaskNameMap  = NewType('TaskNameMap',  Dict[TaskName, TaskId])
