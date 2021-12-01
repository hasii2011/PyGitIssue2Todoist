
from typing import Callable
from typing import Dict
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from todoist import TodoistAPI
from todoist.api import SyncError
from todoist.models import Item
from todoist.models import Note
from todoist.models import Project

from gittodoistclone.adapters.AdapterAuthenticationError import AdapterAuthenticationError

from gittodoistclone.adapters.TodoistAdapterTypes import CloneInformation
from gittodoistclone.adapters.TodoistAdapterTypes import TaskInfo

from gittodoistclone.general.GitHubURLOption import GitHubURLOption

from gittodoistclone.general.Preferences import Preferences
from gittodoistclone.general.exceptions.NoteCreationError import NoteCreationError
from gittodoistclone.general.exceptions.TaskCreationError import TaskCreationError

Tasks             = NewType('Tasks', List[Item])
ProjectName       = NewType('ProjectName', str)
ProjectDictionary = NewType('ProjectDictionary', Dict[ProjectName, Project])


class AbstractTodoistAdapter:

    clsLogger: Logger = getLogger(__name__)

    def __init__(self, apiToken: str):
        """

        Args:
            apiToken: The login token for the todoist API
        """
        self._todoist:     TodoistAPI  = TodoistAPI(apiToken)
        self._preferences: Preferences = Preferences()
        self._devTasks:    Tasks       = Tasks([])

    def createTasks(self, info: CloneInformation, progressCb: Callable):
        """
        Abstract method;  Subclass must implement
        Args:
            info:           The Clone information from the GitHub calls
            progressCb:     The callback to report information
        """
        pass

    def _determineProjectIdFromRepoName(self, info: CloneInformation, progressCb: Callable) -> int:
        """
        Either gets a project ID from the repo name or one for the user specified project

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status

        Returns:  An appropriate parent ID for newly created tasks
        """
        pass

    def _createItemNameMap(self, items) -> Dict[str, int]:

        itemMap: Dict[str, int] = {}
        for item in items:
            itemName: str = item['content']
            itemId:   int = item['id']

            itemMap[itemName] = itemId
            AbstractTodoistAdapter.clsLogger.warning(f'TaskName: {item["content"]}')

        return itemMap

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
            # Might have name embedded as URL
            if taskInfo.gitIssueName in taskItem['content']:
                foundTaskItem = taskItem
                break
        #
        # To create subtasks first create in project then move them to the milestone task
        #
        if foundTaskItem is None:
            option: GitHubURLOption = self._preferences.githubURLOption
            if option == GitHubURLOption.DoNotAdd:
                subTask: Item = todoist.items.add(taskInfo.gitIssueName, project_id=projectId)
            elif option == GitHubURLOption.AddAsDescription:
                subTask = todoist.items.add(taskInfo.gitIssueName, project_id=projectId, description=taskInfo.gitIssueURL)
            elif option == GitHubURLOption.AddAsComment:
                subTask = todoist.items.add(taskInfo.gitIssueName, project_id=projectId)
                taskId: int = subTask["id"]
                note: Note = self._addNoteToTask(itemId=taskId, noteContent=taskInfo.gitIssueURL)
                AbstractTodoistAdapter.clsLogger.info(f'Note added: {note}')
            else:   # Add as hyper link
                linkedTaskName: str = f'[{taskInfo.gitIssueName}]({taskInfo.gitIssueURL})'
                subTask = todoist.items.add(linkedTaskName, project_id=projectId)

            subTask.move(parent_id=parentMileStoneTaskItem['id'])

    def _addNoteToTask(self, itemId: int, noteContent: str) -> Note:
        """
        Currently only support creating text notes

        Args:
            itemId:         The id of the task to add this note to
            noteContent:    The content of the note

        Returns:  The created Note time
        """

        todoist: TodoistAPI = self._todoist
        try:
            note:     Note           = todoist.notes.add(itemId, noteContent)
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

    def _getCurrentProjects(self) -> ProjectDictionary:

        todoist: TodoistAPI = self._todoist
        todoist.sync()

        projects: List[Project] = todoist.state['projects']

        projectDictionary: ProjectDictionary = ProjectDictionary({})

        for aProject in projects:

            project: Project = cast(Project, aProject)

            projectName: ProjectName = project["name"]
            projectId:   int = project['id']

            AbstractTodoistAdapter.clsLogger.debug(f'{projectName:12} - {projectId=}')

            projectDictionary[projectName] = project

        return projectDictionary

    def _createProject(self, name: ProjectName) -> Project:

        project: Project = self._todoist.projects.add(name)

        return project

    def _synchronize(self, progressCb):
        """
        Call todoist API to synchronize local results.  Does error handling

        Args:
            progressCb: The callback to which we report progress
        """

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
                eMsg: str = eDict['error']
                eCode: int = eDict['error_code']

                taskCreationError: TaskCreationError = TaskCreationError()
                taskCreationError.message = eMsg
                taskCreationError.errorCode = eCode

                raise taskCreationError

        progressCb('Done')
