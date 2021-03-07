
from typing import List
from typing import Callable
from typing import NewType
from typing import cast
from typing import Dict

from dataclasses import dataclass
from dataclasses import field

from logging import Logger
from logging import getLogger

from todoist import TodoistAPI
from todoist.models import Item
from todoist.models import Project

from gittodoistclone.adapters.AdapterAuthenticationError import AdapterAuthenticationError


@dataclass
class CloneInformation:
    repositoryTask:    str = ''
    milestoneNameTask: str = ''
    tasksToClone:      List[str] = field(default_factory=list)


ProjectName       = NewType('ProjectName', str)
ProjectDictionary = NewType('ProjectDictionary', Dict[ProjectName, Project])
Tasks             = NewType('Projects', List[Item])


@dataclass
class ProjectTasks:
    mileStoneTasks: Tasks = field(default_factory=list)
    devTasks:       Tasks = field(default_factory=list)


class TodoistAdapter:

    def __init__(self, apiToken: str):

        self.logger:             Logger            = getLogger(__name__)
        self._todoist:           TodoistAPI        = TodoistAPI(apiToken)
        self._projectDictionary: ProjectDictionary = ProjectDictionary({})

    def createTasks(self, info: CloneInformation, progressCb: Callable):
        """

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status
        """

        self.logger.info(f'{progressCb.__name__} - {info=}')

        todoist: TodoistAPI = self._todoist

        progressCb('Starting')

        projectId = self._determineProjectIdFromRepoName(info, progressCb)

        milestoneTaskItem: Item = self._getMilestoneTaskItem(projectId=projectId, milestoneNameTask=info.milestoneNameTask, progressCb=progressCb)

        tasks: List[str] = info.tasksToClone
        #
        # To create subtasks first create in project then move them to the milestone task
        #
        for task in tasks:
            subTask: Item = todoist.items.add(task, project_id=projectId)
            subTask.move(parent_id=milestoneTaskItem['id'])

        progressCb('Start Sync')
        response: Dict[str, str] = self._todoist.sync()
        if "error_tag" in response:
            raise AdapterAuthenticationError(response)
        else:
            progressCb('Committing')
            self._todoist.commit()
            progressCb('Done')

    def _determineProjectIdFromRepoName(self, info: CloneInformation, progressCb: Callable):
        """

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status
        """

        self._projectDictionary = self._getCurrentProjects()

        justRepoName:       str = info.repositoryTask.split('/')[1]
        projectId:          int = self._getProjectId(projectName=ProjectName(justRepoName), projectDictionary=self._projectDictionary)

        progressCb(f'Added {justRepoName}')

        return projectId

    def _getProjectId(self, projectName: ProjectName, projectDictionary: ProjectDictionary) -> int:
        """
        Either returns an existing project ID or creates a project and
        Args:
            projectName:        The project name we are searching for
            projectDictionary:  A pre-built dictionary

        Returns:
            A todoist project id
        """

        if projectName in projectDictionary:
            project: Project = projectDictionary[projectName]
        else:
            project: Project = self._createProject(projectName)

        projectId: int = project['id']

        return projectId

    def _getMilestoneTaskItem(self, projectId: int, milestoneNameTask: str, progressCb: Callable) -> Item:

        todoist: TodoistAPI = self._todoist

        # noinspection PyUnusedLocal
        projectTasks: ProjectTasks = self._getProjectTaskItems(projectId=projectId)

        milestoneTaskItem: Item = cast(Item, None)
        mileStoneTaskItems: Tasks = projectTasks.mileStoneTasks
        for taskItem in mileStoneTaskItems:
            self.logger.warning(f'MileStone Task: {taskItem["content"]}')
            if taskItem['content'] == milestoneNameTask:
                milestoneTaskItem = taskItem
                progressCb(f'Found existing milestone: {milestoneNameTask}')
                break

        if milestoneTaskItem is None:
            milestoneTaskItem = todoist.items.add(milestoneNameTask, project_id=projectId)
            progressCb(f'Added milestone: {milestoneNameTask}')

        return milestoneTaskItem

    def _createProject(self, name: ProjectName) -> Project:

        project: Project = self._todoist.projects.add(name)

        return project

    def _getCurrentProjects(self) -> ProjectDictionary:

        todoist: TodoistAPI = self._todoist
        todoist.sync()

        projects: List[Project] = todoist.state['projects']

        projectDictionary: ProjectDictionary = ProjectDictionary({})

        for project in projects:

            project: Project = cast(Project, project)

            projectName: str = project["name"]
            projectId:   int = project['id']

            self.logger.debug(f'{projectName:12} - {projectId=}')

            projectDictionary[projectName] = project

        return projectDictionary

    def _getProjectTaskItems(self, projectId: int) -> ProjectTasks:
        """

        Args:
            projectId:  The project ID from which we need its task lists

        Returns: A tuple of two lists;  The first are the milestone tasks;  The second are
        potential child tasks whose parents are one of the milestone tasks

        """

        todoist: TodoistAPI = self._todoist
        dataItems: Dict[str, Item] = todoist.projects.get_data(project_id=projectId)

        # noinspection PyTypeChecker
        mileStoneTasks: Tasks = Tasks([])
        devTasks:       Tasks = Tasks([])

        try:
            # noinspection PyTypeChecker
            items: List[Item] = dataItems['items']
            for item in items:

                parentId: int = item["parent_id"]
                self.logger.warning(f'{item["content"]=}  {item["id"]=} {parentId=}')

                if parentId is None:
                    mileStoneTasks.append(item)
                else:
                    devTasks.append(item)
        except KeyError:
            self.logger.warning('No items means this is a new project')

        projectTasks: ProjectTasks = ProjectTasks(mileStoneTasks=mileStoneTasks, devTasks=devTasks)

        return projectTasks
