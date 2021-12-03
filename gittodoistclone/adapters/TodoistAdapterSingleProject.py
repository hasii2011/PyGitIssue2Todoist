from typing import Dict
from typing import List

from collections import Callable

from logging import Logger
from logging import getLogger

from todoist import TodoistAPI
from todoist.managers.projects import ProjectsManager
from todoist.models import Item

from gittodoistclone.adapters.AbstractTodoistAdapter import AbstractTodoistAdapter
from gittodoistclone.adapters.AbstractTodoistAdapter import ProjectName
from gittodoistclone.adapters.AbstractTodoistAdapter import Tasks

from gittodoistclone.adapters.TodoistAdapter import ProjectData
from gittodoistclone.adapters.TodoistAdapterTypes import CloneInformation
from gittodoistclone.adapters.TodoistAdapterTypes import TaskInfo


class TodoistAdapterSingleProject(AbstractTodoistAdapter):

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
        self.logger.info(f'{progressCb.__name__} - {info=}')

        progressCb('Starting')

        projectId: int = self._determineProjectIdFromRepoName(info, progressCb)

        self._createTasksInParentProject(info, progressCb, projectId)

        self._synchronize(progressCb=progressCb)

    def _determineProjectIdFromRepoName(self, info: CloneInformation, progressCb: Callable) -> int:
        """
        Implement empty method from parent;
        Gets a project ID for the user specified project

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status

        Returns:  A project parent id
        """
        self._projectDictionary = self._getCurrentProjects()

        projectName: ProjectName = ProjectName(self._preferences.todoistProjectName)
        projectId:   int         = self._getProjectId(projectName=projectName, projectDictionary=self._projectDictionary)

        progressCb(f'Using parent project: {self._preferences.todoistProjectName}')

        return projectId

    def _createTasksInParentProject(self, info, progressCb, projectId):
        """

        Args:
            info:
            progressCb:
            projectId:
        """
        tasks:     List[TaskInfo] = info.tasksToClone

        justRepoName:      str  = info.repositoryTask.split('/')[1]
        repoTaskId:        int  = self._getIdForRepoName(parentId=projectId, repoName=justRepoName)
        milestoneTaskItem: Item = self._getMileStoneTaskFromParentTask(projectId=projectId, repoTaskId=repoTaskId,
                                                                       milestoneName=info.milestoneNameTask, progressCb=progressCb)

        milestoneId: int = milestoneTaskItem['id']
        self._devTasks = self._findAllSubTasksOfMilestoneTask(projectId=projectId, milestoneId=milestoneId)
        for taskInfo in tasks:
            self._createTaskItem(taskInfo=taskInfo, projectId=milestoneId, parentMileStoneTaskItem=milestoneTaskItem)

    def _getIdForRepoName(self, parentId: int, repoName: str) -> int:

        projectData: Dict = self._todoist.projects.get_data(parentId)
        items:       List = projectData['items']

        itemNames: Dict[str, int] = self._createItemNameMap(items=items)

        # Either use the id of the one found or create it
        if repoName in itemNames:
            repoId: int = itemNames[repoName]
        else:
            todoist:  TodoistAPI = self._todoist
            repoTask: Item       = todoist.items.add(repoName, project_id=parentId)

            repoTask.move(project_id=parentId)
            repoId = repoTask['id']

        return repoId

    def _getMileStoneTaskFromParentTask(self, projectId: int, repoTaskId: int, milestoneName: str, progressCb: Callable) -> Item:
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

        projectData: Dict = self._todoist.projects.get_data(project_id=projectId)
        items:       List = projectData['items']

        itemNames: Dict[str, int] = self._createItemNameMap(items=items)

        if milestoneName in itemNames:
            singleItemList: List = [x for x in items if x['content'] == milestoneName]
            progressCb(f'Found existing milestone: {milestoneName}')
            milestoneTaskItem: Item = singleItemList[0]
        else:
            milestoneTaskItem = todoist.items.add(milestoneName, project_id=projectId)
            progressCb(f'Added milestone: {milestoneName}')
            milestoneTaskItem.move(parent_id=repoTaskId)

        return milestoneTaskItem

    def _findAllSubTasksOfMilestoneTask(self, projectId: int, milestoneId: int) -> Tasks:
        """

        Args:
            projectId:  The Id of the parent task where all GitHub tasks reside
            milestoneId:    The milestone task Id

        Returns:
            The list of subtasks that are leaf tasks end of the projectId->repoTaskId->milestoneId task branch
        """
        subTasks: Tasks = Tasks([])

        todoist:   TodoistAPI  = self._todoist

        projectsManager: ProjectsManager = todoist.projects

        dataItems: ProjectData = projectsManager.get_data(project_id=projectId)
        items: List[Item] = dataItems['items']

        for item in items:
            parentId: int = item["parent_id"]
            self.logger.debug(f'{item["content"]=}  {item["id"]=} {parentId=}')
            if parentId == milestoneId:
                subTasks.append(item)

        return subTasks
