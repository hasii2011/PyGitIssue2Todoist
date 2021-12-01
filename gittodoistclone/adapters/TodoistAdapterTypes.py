
from typing import List

from dataclasses import dataclass
from dataclasses import field
from typing import NewType

from todoist.models import Item


@dataclass
class TaskInfo:
    gitIssueName: str = ''
    gitIssueURL:  str = ''


@dataclass
class CloneInformation:
    repositoryTask:    str = ''
    milestoneNameTask: str = ''
    tasksToClone:      List[TaskInfo] = field(default_factory=list)
