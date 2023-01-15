
from typing import List

from dataclasses import dataclass
from dataclasses import field


@dataclass
class GitIssueInfo:
    gitIssueName: str = ''
    gitIssueURL:  str = ''


@dataclass
class CloneInformation:
    repositoryTask:    str = ''
    milestoneNameTask: str = ''
    tasksToClone:      List[GitIssueInfo] = field(default_factory=list)
