
from logging import Logger
from logging import getLogger
from typing import Callable
from typing import Dict
from typing import List
from typing import NewType
from typing import cast

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

from pygitissue2todoist.strategy.AbstractTodoistStrategy import AbstractTodoistStrategy
from pygitissue2todoist.strategy.TodoistStrategyTypes import CloneInformation
from pygitissue2todoist.strategy.TodoistStrategyTypes import GitIssueInfo
from pygitissue2todoist.strategy.TodoistStrategyTypes import TaskId
from pygitissue2todoist.strategy.TodoistStrategyTypes import TaskName
from pygitissue2todoist.strategy.TodoistStrategyTypes import TaskNameMap
from pygitissue2todoist.strategy.TodoistStrategyTypes import Tasks

RepositoryId = NewType('RepositoryId', str)

TaskList   = List[Task]
SubTaskMap = NewType('SubTaskMap',  Dict[TaskName, TaskId])

RepositoryName           = NewType('RepositoryName', str)


class TodoistOwnerIssues(AbstractTodoistStrategy):
    """
    This strategy relies on a GitHub issue selection strategy that collects a developer's open
    issue across all repositories and organizations

    """
    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)

        self._repositoryTaskMap: TaskNameMap = cast(TaskNameMap, None)

    def createTasks(self, info: CloneInformation, progressCb: Callable):

        self._infoLogCloneInformation(info=info, progressCb=progressCb)

        progressCb('Starting')

        projectId: str = self._determineTopLevelProjectId(info, progressCb)

        self._createProjectTasksInTopLevelProject(info=info, progressCb=progressCb, projectId=projectId)

    def _determineTopLevelProjectId(self, info: CloneInformation, progressCb: Callable) -> str:

        projectId: str = self._getProjectIdOfSingleProjectName(progressCb=progressCb)
        return projectId

    def _createProjectTasksInTopLevelProject(self, info, progressCb: Callable, projectId: str):
        """

        Args:
            info:
            progressCb:
            projectId:
        """

        self._devTasks = Tasks(self._todoist.get_tasks(project_id=projectId))
        # This includes all the repository tasks and repository subtasks (ugh)
        #
        self._repositoryTaskMap = self._createTaskNameMap(tasks=self._devTasks)
        #
        # Iterate through all the clone issues
        #
        cloneIssues: List[GitIssueInfo] = info.tasksToClone
        for cloneIssue in cloneIssues:
            gitIssueInfo: GitIssueInfo = cast(GitIssueInfo, cloneIssue)
            justRepoName: str          = gitIssueInfo.slug.split('/')[1]
            todoist:      TodoistAPI   = self._todoist
            #
            # Do not recreate the repository task if it already exists
            #
            if justRepoName in self._repositoryTaskMap.keys():
                repoId: str = self._repositoryTaskMap[TaskName(justRepoName)]
                progressCb(f'Found existing repository task: {justRepoName}')
                repoTask: Task = todoist.get_task(task_id=repoId)
            else:
                repoTask = todoist.add_task(project_id=projectId, content=justRepoName, description='Repository task created by PyGitIssue2Todoist')
                progressCb(f'Created new repository task: {justRepoName}')
                #
                # Since we created a new repository task put it in the name map
                #
                self._repositoryTaskMap[TaskName(repoTask.content)] = TaskId(repoTask.id)

            self._createTaskItem(
                gitIssueInfo=gitIssueInfo,
                projectId=projectId,
                parentTaskItem=repoTask,
                progressCb=progressCb
            )

    def _getRepositorySubTasks(self, repoId: RepositoryId, projectTopLevelTasks: TaskList) -> SubTaskMap:

        subTaskMap: SubTaskMap = SubTaskMap({})
        for t in projectTopLevelTasks:
            task: Task = cast(Task, t)
            if task.parent_id == repoId:
                self.logger.info(f'Task {task.content} exists')
                subTaskMap[TaskName(task.content)] = TaskId(task.id)

        return subTaskMap
