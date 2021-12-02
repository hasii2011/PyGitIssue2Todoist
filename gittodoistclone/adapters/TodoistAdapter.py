
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

from todoist import TodoistAPI

from todoist.managers.projects import ProjectsManager

from todoist.models import Item
from todoist.models import Project

from gittodoistclone.adapters.AbstractTodoistAdapter import AbstractTodoistAdapter
from gittodoistclone.adapters.AbstractTodoistAdapter import ProjectDictionary
from gittodoistclone.adapters.AbstractTodoistAdapter import ProjectName
from gittodoistclone.adapters.AbstractTodoistAdapter import Tasks


from gittodoistclone.adapters.TodoistAdapterTypes import CloneInformation
from gittodoistclone.adapters.TodoistAdapterTypes import TaskInfo


@dataclass
class ProjectTasks:
    # Figure this out later...
    # Incompatible types in assignment (expression has type "List[_T]", variable has type "Tasks")
    mileStoneTasks: Tasks = field(default_factory=list)     # type: ignore
    devTasks:       Tasks = field(default_factory=list)     # type: ignore


Items            = NewType('Items', Dict[str, str])
ProjectNotes     = NewType('ProjectNotes', List[str])
Sections         = NewType('Sections', List[str])

ProjectDataTypes = NewType('ProjectDataTypes', Union[Items, Project, ProjectNotes, Sections])   # type: ignore

ProjectData = NewType('ProjectData', Dict[str, ProjectDataTypes])


class TodoistAdapter(AbstractTodoistAdapter):

    def __init__(self, apiToken: str):

        super().__init__(apiToken=apiToken)

        self.logger:             Logger            = getLogger(__name__)
        # self._todoist:           TodoistAPI        = TodoistAPI(apiToken)
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

        projectId:         int  = self._determineProjectIdFromRepoName(info, progressCb)
        milestoneTaskItem: Item = self._getMilestoneTaskItem(projectId=projectId, milestoneNameTask=info.milestoneNameTask, progressCb=progressCb)

        tasks: List[TaskInfo] = info.tasksToClone
        for taskInfo in tasks:
            self._createTaskItem(taskInfo=taskInfo, projectId=projectId, parentMileStoneTaskItem=milestoneTaskItem)

        self._synchronize(progressCb)

    def _determineProjectIdFromRepoName(self, info: CloneInformation, progressCb: Callable) -> int:
        """
        Either gets a project ID from the repo name or one for the user specified project

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status

        Returns:  An appropriate parent ID for newly created tasks
        """
        self._projectDictionary = self._getCurrentProjects()

        if self._preferences.tasksInParentProject is True:
            projectName: ProjectName = ProjectName(self._preferences.parentProjectName)
            projectId:   int         = self._getProjectId(projectName=projectName, projectDictionary=self._projectDictionary)
            progressCb(f'Using parent project: {self._preferences.parentProjectName}')
        else:
            justRepoName: str = info.repositoryTask.split('/')[1]
            projectId = self._getProjectId(projectName=ProjectName(justRepoName), projectDictionary=self._projectDictionary)

            progressCb(f'Added {justRepoName}')

        return projectId

    def _getMilestoneTaskItem(self, projectId: int, milestoneNameTask: str, progressCb: Callable) -> Item:
        """
        Has the side effect that it sets self._devTasks

        Args:
            projectId:          The project to search under
            milestoneNameTask:  The name of the milestone task
            progressCb:         The callback to report status to

        Returns:  Either an existing milestone task or a newly created one
        """

        todoist: TodoistAPI = self._todoist

        # noinspection PyUnusedLocal
        projectTasks   = self._getProjectTaskItems(projectId=projectId)
        self._devTasks = projectTasks.devTasks

        milestoneTaskItem:  Item  = cast(Item, None)
        mileStoneTaskItems: Tasks = projectTasks.mileStoneTasks
        for taskItem in mileStoneTaskItems:
            self.logger.debug(f'MileStone Task: {taskItem["content"]}')
            if taskItem['content'] == milestoneNameTask:
                milestoneTaskItem = taskItem
                progressCb(f'Found existing milestone: {milestoneNameTask}')
                break
        # if none found create new one
        if milestoneTaskItem is None:
            milestoneTaskItem = todoist.items.add(milestoneNameTask, project_id=projectId)
            progressCb(f'Added milestone: {milestoneNameTask}')

        return milestoneTaskItem

    def _getProjectTaskItems(self, projectId: int) -> ProjectTasks:
        """

        Args:
            projectId:  The project ID from which we need its task lists or an id
            of a parent task

        Returns: A tuple of two lists;  The first are the milestone tasks;  The second are
        potential child tasks whose parents are one of the milestone tasks
        """

        todoist:   TodoistAPI  = self._todoist

        projectsManager: ProjectsManager = todoist.projects
        dataItems: ProjectData = projectsManager.get_data(project_id=projectId)

        mileStoneTasks: Tasks = Tasks([])
        devTasks:       Tasks = Tasks([])

        try:
            # noinspection PyTypeChecker
            items: List[Item] = dataItems['items']
            for item in items:

                parentId: int = item["parent_id"]
                self.logger.debug(f'{item["content"]=}  {item["id"]=} {parentId=}')

                if parentId is None:
                    mileStoneTasks.append(item)
                else:
                    devTasks.append(item)
        except KeyError:
            self.logger.warning('No items means this is a new project')

        projectTasks: ProjectTasks = ProjectTasks(mileStoneTasks=mileStoneTasks, devTasks=devTasks)

        return projectTasks

    def _getIdForRepoName(self, parentId: int, repoName: str) -> int:

        projectData: Dict = self._todoist.projects.get_data(parentId)
        items:       List = projectData['items']

        itemNames: Dict[str, int] = self._createItemNameMap(items=items)

        # Either use the id of the one found or create it
        if repoName in itemNames:
            repoId: int = itemNames[repoName]
        else:
            todoist: TodoistAPI = self._todoist
            repoTask: Item = todoist.items.add(repoName, project_id=parentId)
            repoTask.move(project_id=parentId)
            repoId = repoTask['id']

        return repoId
