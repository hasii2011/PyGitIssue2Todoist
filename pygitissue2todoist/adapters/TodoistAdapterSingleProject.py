
from typing import cast
from typing import Dict
from typing import List
from typing import Callable

from logging import Logger
from logging import getLogger
from logging import INFO

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

from pygitissue2todoist.adapters.AbstractTodoistAdapter import AbstractTodoistAdapter
from pygitissue2todoist.adapters.AbstractTodoistAdapter import ProjectName
from pygitissue2todoist.adapters.AbstractTodoistAdapter import Tasks

from pygitissue2todoist.adapters.TodoistAdapterTypes import CloneInformation
from pygitissue2todoist.adapters.TodoistAdapterTypes import GitIssueInfo


class TodoistAdapterSingleProject(AbstractTodoistAdapter):
    """
    This version of the adapter creates repository sub-tasks inside a single top level project.  This allows
    users who are using the "community" version of Todoist to create sub-tasks for all their repositories inside
    a single task.  'Community' users are limited to 5 Todoist projects
    """

    def __init__(self, apiToken: str):
        """

        Args:
            apiToken: The login token for the todoist API
        """
        super().__init__(apiToken=apiToken)
        self.logger: Logger = getLogger(__name__)

    def createTasks(self, info: CloneInformation, progressCb: Callable):
        """
        Abstract method;  Subclass must implement
        Args:
            info:           The Clone information from the GitHub calls
            progressCb:     The callback to report information
        """
        self._infoLogCloneInformation(info=info, progressCb=progressCb)

        progressCb('Starting')

        projectId: str = self._determineProjectIdFromRepoName(info, progressCb)

        self._createTasksInParentProject(info, progressCb, projectId)

        self._synchronize(progressCb=progressCb)

    def _determineProjectIdFromRepoName(self, info: CloneInformation, progressCb: Callable) -> str:
        """
        Implement abstract method from parent;
        Gets a project ID for the user specified project

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status

        Returns:  A project parent id
        """
        self._projectDictionary = self._getCurrentProjects()

        projectName: ProjectName = ProjectName(self._preferences.todoistProjectName)
        projectId:   str         = self._getProjectId(projectName=projectName, projectDictionary=self._projectDictionary)

        progressCb(f'Using parent project: {self._preferences.todoistProjectName}')

        return projectId

    def _createTasksInParentProject(self, info, progressCb, projectId):
        """

        Args:
            info:
            progressCb:
            projectId:
        """
        tasks:     List[GitIssueInfo] = info.tasksToClone

        justRepoName:      str  = info.repositoryTask.split('/')[1]
        repoTaskId:        str  = self._getIdForRepoName(projectId=projectId, repoName=justRepoName)
        milestoneTaskItem: Task = self._createMileStoneTaskUnderRepoTask(projectId=projectId,
                                                                         repoTaskId=repoTaskId,
                                                                         milestoneName=info.milestoneNameTask,
                                                                         progressCb=progressCb)

        milestoneId: str = milestoneTaskItem.id
        self._devTasks = self._findAllSubTasksOfMilestoneTask(projectId=projectId, milestoneId=milestoneId)
        for taskInfo in tasks:
            self._createTaskItem(taskInfo=taskInfo, projectId=milestoneId, parentMileStoneTaskItem=milestoneTaskItem)

    def _getIdForRepoName(self, projectId: str, repoName: str) -> str:
        """
        Will either find a repo in the "development" task or create it in the "development" task
        Args:
            projectId:
            repoName:

        Returns: The Repo ID

        """
        # projectData: Dict = self._todoist.projects.get_data(parentId)
        tasks = self._todoist.get_tasks(project_id=projectId)
        # items:       List = projectData['items']

        itemNames: Dict[str, str] = self._createTaskNameMap(tasks=tasks)

        # Either use the id of the one found or create it
        if repoName in itemNames:
            repoId: str = itemNames[repoName]
        else:
            todoist:  TodoistAPI = self._todoist
            repoTask: Task = todoist.add_task(project_id=projectId, content=repoName, description='Repo task created by PyGitIssue2Todoist')

            repoId = repoTask.id

        return repoId

    def _createMileStoneTaskUnderRepoTask(self, projectId: str, repoTaskId: str, milestoneName: str, progressCb: Callable) -> Task:
        """

        Args:
            projectId:      The id of the parent project
            repoTaskId:     The id of the repo task under parent project
            milestoneName:  The milestone name under the repo task;
            progressCb:     The callback to report status to

        Returns:  Either an existing milestone task or a newly created one
        """
        progressCb(f'Retrieving milestone task: {milestoneName}')
        todoist: TodoistAPI = self._todoist

        tasks = self._todoist.get_tasks(project_id=projectId)

        itemNames: Dict[str, str] = self._createTaskNameMap(tasks=tasks)

        if milestoneName in itemNames:
            singleItemList: List = [x for x in tasks if x.content == milestoneName]
            msg: str = f'Using existing milestone: {milestoneName}'
            progressCb(msg)
            milestoneTask: Task = singleItemList[0]
            self.logger.info(msg)
        else:
            debugDescription: str = f"{projectId=} {repoTaskId=}"
            milestoneTask = todoist.add_task(project_id=projectId,
                                             parent_id=repoTaskId,
                                             content=milestoneName,
                                             description=debugDescription)
            msg = f'Added milestone: {milestoneName}'
            progressCb(msg)
            self.logger.info(msg)

        return milestoneTask

    def _findAllSubTasksOfMilestoneTask(self, projectId: str, milestoneId: str) -> Tasks:
        """

        Args:
            projectId:  The id of the parent task where all GitHub tasks reside
            milestoneId:    The milestone task id

        Returns:
            The list of subtasks that are leaf tasks end of the projectId->repoTaskId->milestoneId task branch
        """
        subTasks: Tasks = Tasks([])

        todoist:   TodoistAPI  = self._todoist

        # projectsManager: ProjectsManager = todoist.projects

        # dataItems: ProjectData = projectsManager.get_data(project_id=projectId)
        #  tasks = await todoist_api_async.get_tasks(project_id=project_id, label_id=label_id, filter=filter, lang=lang, ids=ids)
        # items: List[Item] = dataItems['items']
        tasks = todoist.get_tasks(project_id=projectId)

        for item in tasks:
            task: Task = cast(Task, item)
            # parentId: int = item["parent_id"]
            parentId: str = task.parent_id  # type: ignore
            self.logger.debug(f'{task.content=}  {task.id=} {parentId=}')
            if parentId == milestoneId:
                subTasks.append(item)

        return subTasks

    def _infoLogCloneInformation(self, info: CloneInformation, progressCb: Callable):

        if self.logger.isEnabledFor(INFO) is True:
            self.logger.info(f'{progressCb.__name__}')

            self.logger.info(f'{info.repositoryTask=} {info.milestoneNameTask=}')
            for t in info.tasksToClone:
                gitIssueInfo: GitIssueInfo = cast(GitIssueInfo, t)
                self.logger.info(f'{gitIssueInfo.gitIssueName}')
