
from typing import List
from typing import Callable
from typing import NewType
from typing import Union
from typing import cast
from typing import Dict

from dataclasses import dataclass
from dataclasses import field

from logging import Logger
from logging import getLogger

from todoist_api_python.api import TodoistAPI

from todoist_api_python.models import Project
from todoist_api_python.models import Task

from pygitissue2todoist.strategy.AbstractTodoistStrategy import AbstractTodoistStrategy

from pygitissue2todoist.strategy.TodoistStrategyTypes import CloneInformation
from pygitissue2todoist.strategy.TodoistStrategyTypes import GitIssueInfo
from pygitissue2todoist.strategy.TodoistStrategyTypes import ProjectDictionary
from pygitissue2todoist.strategy.TodoistStrategyTypes import ProjectName
from pygitissue2todoist.strategy.TodoistStrategyTypes import Tasks
from pygitissue2todoist.strategy.TodoistStrategyTypes import tasksFactory


@dataclass
class ProjectTasks:
    mileStoneTasks: Tasks = field(default_factory=tasksFactory)
    devTasks:       Tasks = field(default_factory=tasksFactory)


Items            = NewType('Items', Dict[str, str])
ProjectNotes     = NewType('ProjectNotes', List[str])
Sections         = NewType('Sections', List[str])

ProjectDataTypes = NewType('ProjectDataTypes', Union[Items, Project, ProjectNotes, Sections])   # type: ignore

ProjectData = NewType('ProjectData', Dict[str, ProjectDataTypes])


class TodoistCreateByRepository(AbstractTodoistStrategy):
    """
    This version of the adapter creates projects for each GitHub repository.  This is
    ideal for users who have purchased a Todoist license which allows unlimited projects
    """

    def __init__(self):

        super().__init__()

        self.logger:             Logger            = getLogger(__name__)
        # self._preferences:       Preferences       = Preferences()
        # self._devTasks:          Tasks             = Tasks([])

        self._projectDictionary: ProjectDictionary = ProjectDictionary({})

    def createTasks(self, info: CloneInformation, progressCb: Callable):
        """

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status
        """
        self.logger.info(f'{progressCb.__name__} - {info=}')

        progressCb('Starting')

        projectId:         str  = self._determineProjectIdFromRepoName(info, progressCb)
        milestoneTaskItem: Task = self._getMilestoneTaskItem(projectId=projectId, milestoneName=info.milestoneNameTask, progressCb=progressCb)

        tasks: List[GitIssueInfo] = info.tasksToClone
        for taskInfo in tasks:
            self._createTaskItem(taskInfo=taskInfo, projectId=projectId, parentMileStoneTaskItem=milestoneTaskItem)

        self._synchronize(progressCb)

    def _determineProjectIdFromRepoName(self, info: CloneInformation, progressCb: Callable) -> str:
        """
        Implement empty method from parent;
        Gets a project ID from the repo name

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status

        Returns:  An appropriate parent ID for newly created tasks
        """
        self._projectDictionary = self._getCurrentProjects()

        justRepoName: str = info.repositoryTask.split('/')[1]
        projectId:    str = self._getProjectId(projectName=ProjectName(justRepoName), projectDictionary=self._projectDictionary)

        progressCb(f'Added {justRepoName}')

        return projectId

    def _getMilestoneTaskItem(self, projectId: str, milestoneName: str, progressCb: Callable) -> Task:
        """
        Has the side effect that it sets self._devTasks

        Args:
            projectId:      The project to search under
            milestoneName:  The name of the milestone task
            progressCb:     The callback to report status to

        Returns:  Either an existing milestone task or a newly created one
        """
        todoist: TodoistAPI = self._todoist
        projectTasks   = self._getProjectTaskItems(projectId=projectId)
        self._devTasks = projectTasks.devTasks

        milestoneTask:  Task  = cast(Task, None)
        mileStoneTasks: Tasks = projectTasks.mileStoneTasks
        for task in mileStoneTasks:
            self.logger.debug(f'MileStone Task: {task.content=}')
            if task.content == milestoneName:
                milestoneTask = task
                progressCb(f'Found existing milestone: {milestoneName}')
                break
        # if none found create new one
        if milestoneTask is None:
            # milestoneTaskItem = todoist.items.add(milestoneNameTask, project_id=projectId)
            milestoneTask = todoist.add_task(project_id=projectId, content=milestoneName)
            msg: str = f'Added milestone: {milestoneTask}'
            progressCb(msg)
            self.logger.info(msg)

        return milestoneTask

    def _getProjectTaskItems(self, projectId: str) -> ProjectTasks:
        """

        Args:
            projectId:  The project ID from which we need its task lists or an id
            of a parent task

        Returns: A class with two lists;  The first are the milestone tasks;  The second are
        potential child tasks whose parents are one of the milestone tasks
        """

        todoist:   TodoistAPI  = self._todoist

        # TODO:  Get tasks associated with the project
        tasks: List[Task] = todoist.get_tasks(project_id=projectId)
        mileStoneTasks: Tasks = tasksFactory()
        devTasks:       Tasks = tasksFactory()

        try:
            for item in tasks:
                task: Task = cast(Task, item)
                parentId: str = task.parent_id  # type: ignore
                self.logger.debug(f'{task.content=}  {task.id=} {parentId=}')

                if parentId is None:
                    mileStoneTasks.append(item)
                else:
                    devTasks.append(item)
        except KeyError:
            self.logger.warning('No items means this is a new project')

        projectTasks: ProjectTasks = ProjectTasks(mileStoneTasks=mileStoneTasks, devTasks=devTasks)

        return projectTasks
