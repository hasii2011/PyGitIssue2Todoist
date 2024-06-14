
from typing import Callable
from typing import Dict
from typing import List
from typing import NewType
from typing import cast

from abc import ABC
from abc import abstractmethod

from logging import Logger
from logging import getLogger


from todoist_api_python.api import TodoistAPI
from todoist_api_python.api_async import TodoistAPIAsync

from todoist_api_python.models import Project
from todoist_api_python.models import Task
from todoist_api_python.models import Comment

from pygitissue2todoist.adapters.TodoistAdapterTypes import CloneInformation
from pygitissue2todoist.adapters.TodoistAdapterTypes import GitIssueInfo

from pygitissue2todoist.general.GitHubURLOption import GitHubURLOption

from pygitissue2todoist.general.Preferences import Preferences
from pygitissue2todoist.general.exceptions.NoteCreationError import NoteCreationError

Tasks             = NewType('Tasks', List[Task])
ProjectName       = NewType('ProjectName', str)
ProjectDictionary = NewType('ProjectDictionary', Dict[ProjectName, Project])


class AbstractTodoistAdapter(ABC):

    clsLogger: Logger = getLogger(__name__)

    def __init__(self, apiToken: str):
        """
        Initialize common protected properties
        Args:
            apiToken: The login token for the todoist API
        """
        self._todoist:      TodoistAPI      = TodoistAPI(apiToken)
        self._todoistAsync: TodoistAPIAsync = TodoistAPIAsync(apiToken)

        self._preferences: Preferences = Preferences()
        self._devTasks:    Tasks       = Tasks([])

    @abstractmethod
    def createTasks(self, info: CloneInformation, progressCb: Callable):
        """
        Abstract method;  Subclass must implement
        Args:
            info:           The Clone information from the GitHub calls
            progressCb:     The callback to report information
        """
        pass

    @abstractmethod
    def _determineProjectIdFromRepoName(self, info: CloneInformation, progressCb: Callable) -> str:
        """
        Either gets a project ID from the repo name or one for the user specified project

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status

        Returns:  An appropriate parent ID for newly created tasks
        """
        pass

    def _createTaskNameMap(self, tasks: List[Task]) -> Dict[str, str]:
        """

        Args:
            tasks:   Todoist Task

        Returns: dictionary taskName -> id
        """
        taskMap: Dict[str, str] = {}
        for item in tasks:
            task: Task = cast(Task, item)
            # itemName: str = item['content']
            # itemId:   int = item['id']
            itemName: str = task.content
            itemId:   str = task.id

            taskMap[itemName] = itemId
            AbstractTodoistAdapter.clsLogger.debug(f'TaskName: {task.content}')

        return taskMap

    def _createTaskItem(self, taskInfo: GitIssueInfo, projectId: str, parentMileStoneTaskItem: Task):
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

        foundTaskItem: Task = cast(Task, None)
        devTasks:      Tasks = self._devTasks
        for devTask in devTasks:
            taskItem: Task = cast(Task, devTask)
            # Might have name embedded as URL
            # if taskInfo.gitIssueName in taskItem['content']:
            if taskInfo.gitIssueName in taskItem.content:
                foundTaskItem = taskItem
                break
        #
        # To create subtasks first create in project then move them to the milestone task
        # TODO: Make this a case statement in Python 3.10
        #
        if foundTaskItem is None:
            option: GitHubURLOption = self._preferences.githubURLOption
            match option:
                case GitHubURLOption.DoNotAdd:
                    todoist.add_task(projectId=projectId,
                                     parent_id=parentMileStoneTaskItem.id,
                                     content=taskInfo.gitIssueName)
                case GitHubURLOption.AddAsDescription:
                    todoist.add_task(projectId=projectId,
                                     parent_id=parentMileStoneTaskItem.id,
                                     content=taskInfo.gitIssueName,
                                     description=taskInfo.gitIssueURL)
                case GitHubURLOption.AddAsComment:
                    task: Task = todoist.add_task(projectId=projectId,
                                                  parent_id=parentMileStoneTaskItem.id,
                                                  content=taskInfo.gitIssueName)
                    comment: Comment = todoist.add_comment(task_id=task.id, content=taskInfo.gitIssueURL)
                    AbstractTodoistAdapter.clsLogger.info(f'Comment added: {comment}')
                case GitHubURLOption.HyperLinkedTaskName:
                    linkedTaskName: str = f'[{taskInfo.gitIssueName}]({taskInfo.gitIssueURL})'
                    todoist.add_task(project_id=projectId,
                                     parent_id=parentMileStoneTaskItem.id,
                                     content=linkedTaskName)
                case _:
                    self.clsLogger.error(f'Unknown URL option: {option}')

    def _addNoteToTask(self, itemId: str, noteContent: str) -> Comment:
        """
        Currently only support creating text notes

        Args:
            itemId:         The id of the task to add this note to
            noteContent:    The content of the note

        Returns:  The created Note time
        """
        todoist: TodoistAPI = self._todoist
        try:
            newComment = todoist.add_comment(task_id=itemId, content=noteContent)
        except Exception as e:
            eDict = e.args[1]
            eMsg: str = eDict['error']
            eCode: int = eDict['error_code']

            noteCreationError: NoteCreationError = NoteCreationError()
            noteCreationError.message   = eMsg
            noteCreationError.errorCode = eCode

            raise noteCreationError

        return newComment

    def _getProjectId(self, projectName: ProjectName, projectDictionary: ProjectDictionary) -> str:
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
            self.clsLogger.info(f'Using project: {projectName}')
        else:
            project = self._createProject(projectName)
            self.clsLogger.info(f'Created project: {projectName}')

        projectId: str = project.id

        return projectId

    def _getCurrentProjects(self) -> ProjectDictionary:

        todoist: TodoistAPI = self._todoist

        projects: List[Project] = todoist.get_projects()
        projectDictionary: ProjectDictionary = ProjectDictionary({})

        for aProject in projects:

            project: Project = cast(Project, aProject)

            projectName: ProjectName = ProjectName(project.name)
            projectId:   str         = project.id

            AbstractTodoistAdapter.clsLogger.debug(f'{projectName:12} - {projectId=}')

            projectDictionary[projectName] = project

        return projectDictionary

    def _createProject(self, name: ProjectName) -> Project:

        project: Project = self._todoist.add_project(name=name)
        self.clsLogger.info(f'New project: {project.id}')
        return project

    def _synchronize(self, progressCb):
        # TODO: This method is unneeded
        progressCb('Done')
