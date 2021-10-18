
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

from todoist.api import SyncError

from todoist import TodoistAPI

from todoist.managers.projects import ProjectsManager

from todoist.models import Item
from todoist.models import Note
from todoist.models import Project

from gittodoistclone.adapters.AdapterAuthenticationError import AdapterAuthenticationError
from gittodoistclone.general.exceptions.NoteCreationError import NoteCreationError
from gittodoistclone.general.exceptions.TaskCreationError import TaskCreationError


@dataclass
class TaskInfo:
    gitIssueName: str = ''
    gitIssueURL:  str = ''


@dataclass
class CloneInformation:
    repositoryTask:    str = ''
    milestoneNameTask: str = ''
    tasksToClone:      List[TaskInfo] = field(default_factory=list)


ProjectName       = NewType('ProjectName', str)
ProjectDictionary = NewType('ProjectDictionary', Dict[ProjectName, Project])
Tasks             = NewType('Tasks', List[Item])


@dataclass
class ProjectTasks:
    # Figure this out later...
    # Incompatible types in assignment (expression has type "List[_T]", variable has type "Tasks")
    mileStoneTasks: Tasks = field(default_factory=list)     # type: ignore
    devTasks:       Tasks = field(default_factory=list)     # type: ignore


Items            = NewType('Items', Dict[str, str])
# Project          = NewType('Project', Dict[str, str])
ProjectNotes     = NewType('ProjectNotes', List[str])
Sections         = NewType('Sections', List[str])

ProjectDataTypes = NewType('ProjectDataTypes', Union[Items, Project, ProjectNotes, Sections])   # type: ignore

ProjectData = NewType('ProjectData', Dict[str, ProjectDataTypes])


class TodoistAdapter:

    def __init__(self, apiToken: str):

        self.logger:             Logger            = getLogger(__name__)
        self._todoist:           TodoistAPI        = TodoistAPI(apiToken)
        self._projectDictionary: ProjectDictionary = ProjectDictionary({})
        self._devTasks:          Tasks             = Tasks([])

    def createTasks(self, info: CloneInformation, progressCb: Callable):
        """

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status
        """

        self.logger.info(f'{progressCb.__name__} - {info=}')

        # todoist: TodoistAPI = self._todoist

        progressCb('Starting')

        projectId:         int  = self._determineProjectIdFromRepoName(info, progressCb)
        milestoneTaskItem: Item = self._getMilestoneTaskItem(projectId=projectId, milestoneNameTask=info.milestoneNameTask, progressCb=progressCb)

        tasks: List[TaskInfo] = info.tasksToClone
        for taskInfo in tasks:
            self._createTaskItem(taskInfo=taskInfo, projectId=projectId, parentMileStoneTaskItem=milestoneTaskItem)

        progressCb('Start Sync')
        response: Dict[str, str] = self._todoist.sync()
        if "error_tag" in response:
            raise AdapterAuthenticationError(response)
        else:
            progressCb('Committing')
            try:
                self._todoist.commit()
            except SyncError as e:
                eDict = e.args[1]
                eMsg: str  = eDict['error']
                eCode: int = eDict['error_code']

                taskCreationError: TaskCreationError = TaskCreationError()
                taskCreationError.message  = eMsg
                taskCreationError.errorCode = eCode

                raise taskCreationError

            progressCb('Done')

    def addNoteToTask(self, itemId: int, noteContent: str) -> Note:
        """
        Currently only support creating text notes

        Args:
            itemId:         The id of the task to add this note to
            noteContent:    The content of the note

        Returns:  The created Note time
        """

        todoist: TodoistAPI = self._todoist
        try:
            note: Note = todoist.notes.add(itemId, noteContent)
            # note: Note = todoist.notes.add(9999, noteContent)

            response: Dict[str, str] = todoist.commit()

            if "error_tag" in response:
                raise AdapterAuthenticationError(response)
        except SyncError as e:
            eDict = e.args[1]
            eMsg: str = eDict['error']
            eCode: int = eDict['error_code']

            noteCreationError: NoteCreationError = NoteCreationError()
            noteCreationError.message   = eMsg
            noteCreationError.errorCode = eCode

            raise noteCreationError

        return note

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
            project = self._createProject(projectName)

        projectId: int = project['id']

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

    def _createProject(self, name: ProjectName) -> Project:

        project: Project = self._todoist.projects.add(name)

        return project

    def _getCurrentProjects(self) -> ProjectDictionary:

        todoist: TodoistAPI = self._todoist
        todoist.sync()

        projects: List[Project] = todoist.state['projects']

        projectDictionary: ProjectDictionary = ProjectDictionary({})

        for aProject in projects:

            project: Project = cast(Project, aProject)

            projectName: ProjectName = project["name"]
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

        todoist:   TodoistAPI  = self._todoist

        projectsManager: ProjectsManager = todoist.projects
        dataItems:       ProjectData = projectsManager.get_data(project_id=projectId)

        # noinspection PyTypeChecker
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

    def _createTaskItem(self, taskInfo: TaskInfo, projectId: int, parentMileStoneTaskItem: Item):
        """
        Create a new task if it does not already exist in Todoist
        Assumes self._devTasks has all the project's tasks

        Args:
            taskInfo:       The task (with information) to potentially create
            projectId:      Project id of potential task
            parentMileStoneTaskItem: parent item if task needs to be created
        """
        assert self._devTasks is not None, 'Internal error should at least be empty'

        todoist: TodoistAPI = self._todoist

        foundTaskItem: Item = cast(Item, None)
        devTasks:      Tasks = self._devTasks
        for devTask in devTasks:
            taskItem: Item = cast(Item, devTask)
            if taskItem['content'] == taskInfo.gitIssueName:
                foundTaskItem = taskItem
                break
        #
        # To create subtasks first create in project then move them to the milestone task
        #
        if foundTaskItem is None:
            # TODO: when user preference is set add URL as either description or note
            subTask: Item = todoist.items.add(taskInfo.gitIssueName, project_id=projectId, description=taskInfo.gitIssueURL)
            subTask.move(parent_id=parentMileStoneTaskItem['id'])
