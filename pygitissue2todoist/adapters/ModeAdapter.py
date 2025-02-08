from enum import Enum
from todoist_api_python.models import Project
from todoist_api_python.models import Task

from pygitissue2todoist.adapters.TodoistAdapterTypes import GitIssueInfo
from pygitissue2todoist.general.PreferencesV2 import PreferencesV2



class TaskPurpose(Enum):
    """
    This is used to determine the purpose of a task (and hence where it should be placed in Todoist)
    For this a "Todoist Project" is also considered a "Task" as it is relevant to
    the hierarchy of tasks in Todoist.
    """
    Issue = 1
    Milestone = 2
    Repo = 3
    GH_Org = 4
    NamedProject = 5


class Mode(Enum):
    """
    This is used to determine the mode of operation for the adapter
    """
    SingleProjectMilestoneMode = 1
    SingleProjectAssigneeMode = 2
    MultiProjectMilestoneMode = 3
    MultiProjectAssigneeMode = 4


class TodoistTaskInfo:
    """
    This class is used to store information about a task in Todoist
    Specifically information about the way Todoist Tasks are mapped to GitHub Issues
    """
    def __init__(self, gh_issue: GitIssueInfo, task_purpose: TaskPurpose):
        self.gh_issue: GitIssueInfo = gh_issue

        self.task_purpose: TaskPurpose = task_purpose
        self._preferences: PreferencesV2 = PreferencesV2()

    @property
    def _mode(self):
        print(f'{self._preferences.assignmentMode=}')
        if self._preferences.singleTodoistProject:
            return Mode.SingleProjectAssigneeMode if self._preferences.assignmentMode else Mode.SingleProjectMilestoneMode
        else:
            return Mode.MultiProjectAssigneeMode if self._preferences.assignmentMode else Mode.MultiProjectMilestoneMode

    def is_root_task(self) -> bool:
        return self.get_hierarchy[-1] == self.task_purpose

    def get_parent_task_type(self) -> TaskPurpose | None:
        """
        Returns the parent task type for the current task, based on the hierarchy in use.

        If the task is a root task, then the parent task type is None
        """
        idx = self.get_hierarchy.index(self.task_purpose)
        try:
            return self.get_hierarchy[idx + 1]
        except IndexError:
            return None

    @property
    def get_hierarchy(self) -> list[TaskPurpose]:

        all_modes = {
            Mode.MultiProjectMilestoneMode: [
                TaskPurpose.Issue,
                TaskPurpose.Milestone,
                TaskPurpose.Repo,
            ],

            Mode.SingleProjectMilestoneMode: [
                TaskPurpose.Issue,
                TaskPurpose.Milestone,
                TaskPurpose.Repo,
                TaskPurpose.NamedProject,
            ],

            Mode.SingleProjectAssigneeMode: [
                TaskPurpose.Issue,
                TaskPurpose.Repo,
                TaskPurpose.GH_Org,
                TaskPurpose.NamedProject,
            ],

            Mode.MultiProjectAssigneeMode: [
                TaskPurpose.Issue,
                TaskPurpose.Milestone,
                TaskPurpose.Repo,
                TaskPurpose.GH_Org,
            ]
        }

        return all_modes[self._mode]
