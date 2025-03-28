

from typing import List
from typing import cast
from typing import Callable

from abc import ABCMeta

from logging import Logger
from logging import getLogger
from logging import INFO

from todoist_api_python.api import TodoistAPI
from todoist_api_python.api_async import TodoistAPIAsync

from todoist_api_python.models import Project
from todoist_api_python.models import Task
from todoist_api_python.models import Comment

from pygitissue2todoist.strategy.ITodoistCreationStrategy import ITodoistCreationStrategy

from pygitissue2todoist.general.GitHubURLOption import GitHubURLOption

from pygitissue2todoist.general.Preferences import Preferences

from pygitissue2todoist.general.exceptions.NoteCreationError import NoteCreationError
from pygitissue2todoist.strategy.TodoistStrategyTypes import CloneInformation

from pygitissue2todoist.strategy.TodoistStrategyTypes import GitIssueInfo
from pygitissue2todoist.strategy.TodoistStrategyTypes import ProjectDictionary
from pygitissue2todoist.strategy.TodoistStrategyTypes import ProjectName
from pygitissue2todoist.strategy.TodoistStrategyTypes import TaskId
from pygitissue2todoist.strategy.TodoistStrategyTypes import TaskName
from pygitissue2todoist.strategy.TodoistStrategyTypes import TaskNameMap
from pygitissue2todoist.strategy.TodoistStrategyTypes import Tasks


class AbstractTodoistStrategy(ITodoistCreationStrategy, metaclass=ABCMeta):

    clsLogger: Logger = getLogger(__name__)

    def __init__(self):
        """
        Initialize common protected properties
        """
        super().__init__()

        self._preferences: Preferences = Preferences()

        apiToken:           str             = self._preferences.todoistAPIToken
        self._todoist:      TodoistAPI      = TodoistAPI(apiToken)
        self._todoistAsync: TodoistAPIAsync = TodoistAPIAsync(apiToken)

        self._devTasks:          Tasks             = Tasks([])
        self._projectDictionary: ProjectDictionary = ProjectDictionary({})

    def _createTaskNameMap(self, tasks: List[Task]) -> TaskNameMap:
        """

        Args:
            tasks:   Todoist Task

        Returns: dictionary taskName -> id
        """
        taskMap: TaskNameMap = TaskNameMap({})
        for item in tasks:
            task:     Task     = cast(Task, item)
            itemName: TaskName = TaskName(task.content)
            itemId:   TaskId   = TaskId(task.id)

            taskMap[itemName] = itemId
            AbstractTodoistStrategy.clsLogger.debug(f'TaskName: {task.content}')

        return taskMap

    def _createTaskItem(self, gitIssueInfo: GitIssueInfo, projectId: str, parentTaskItem: Task, progressCb: Callable):
        """
        Create a new task if it does not already exist in Todoist
        Assumes self._devTasks has all the project's tasks

        Args:
            gitIssueInfo:       The task (with information) to potentially create
            projectId:      Project id of potential task
            parentTaskItem: parent item if task needs to be created
            progressCb:     Progress callback
        """
        assert self._devTasks is not None, 'Internal error should at least be empty'

        todoist: TodoistAPI = self._todoist

        foundTaskItem: Task = cast(Task, None)
        devTasks:      Tasks = self._devTasks
        for devTask in devTasks:
            taskItem: Task = cast(Task, devTask)
            # Might have name embedded as URL
            # if taskInfo.gitIssueName in taskItem['content']:
            if gitIssueInfo.gitIssueName in taskItem.content:
                foundTaskItem = taskItem
                break
        #
        # To create subtasks first create in project then move them to the milestone task
        #
        if foundTaskItem is None:
            option: GitHubURLOption = self._preferences.gitHubURLOption
            match option:
                case GitHubURLOption.DoNotAdd:
                    todoist.add_task(projectId=projectId,
                                     parent_id=parentTaskItem.id,
                                     content=gitIssueInfo.gitIssueName)

                case GitHubURLOption.AddAsDescription:
                    todoist.add_task(projectId=projectId,
                                     parent_id=parentTaskItem.id,
                                     content=gitIssueInfo.gitIssueName,
                                     description=gitIssueInfo.gitIssueURL)

                case GitHubURLOption.AddAsComment:
                    task: Task = todoist.add_task(projectId=projectId,
                                                  parent_id=parentTaskItem.id,
                                                  content=gitIssueInfo.gitIssueName)
                    comment: Comment = todoist.add_comment(task_id=task.id, content=gitIssueInfo.gitIssueURL)
                    AbstractTodoistStrategy.clsLogger.info(f'Comment added: {comment}')

                case GitHubURLOption.HyperLinkedTaskName:
                    linkedTaskName: str = f'[{gitIssueInfo.gitIssueName}]({gitIssueInfo.gitIssueURL})'
                    todoist.add_task(project_id=projectId,
                                     parent_id=parentTaskItem.id,
                                     content=linkedTaskName)
                case _:
                    self.clsLogger.error(f'Unknown URL option: {option}')
            progressCb(f'Created task: {gitIssueInfo.gitIssueName}')

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

    def _getProjectIdOfSingleProjectName(self, progressCb: Callable):
        """
        Some Todoist strategies place all the subtasks in a single project.  This common method
        returns the ID of that preferred project.

        Args:
            progressCb:  The progress reporting callback

        """
        progressCb(f'Using single project: {self._preferences.todoistProjectName}')

        self._projectDictionary = self._getCurrentProjects()

        projectName: ProjectName = ProjectName(self._preferences.todoistProjectName)
        projectId:   str         = self._getProjectId(projectName=projectName, projectDictionary=self._projectDictionary)

        return projectId

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

    def _getIdForRepoName(self, projectId: str, repoName: str) -> str:
        """
        Will either find a repo in the "development" task or create it in the "development" task
        Args:
            projectId:
            repoName:

        Returns: The Repo ID

        """
        tasks = self._todoist.get_tasks(project_id=projectId)

        itemNames: TaskNameMap = self._createTaskNameMap(tasks=tasks)

        # Either use the id of the one found or create it
        if repoName in itemNames:
            repoId: str = itemNames[TaskName(repoName)]
        else:
            todoist:  TodoistAPI = self._todoist
            repoTask: Task = todoist.add_task(project_id=projectId, content=repoName, description='Repo task created by PyGitIssue2Todoist')

            repoId = repoTask.id

        return repoId

    def _getCurrentProjects(self) -> ProjectDictionary:

        todoist: TodoistAPI = self._todoist

        projects:          List[Project]     = todoist.get_projects()
        projectDictionary: ProjectDictionary = ProjectDictionary({})

        for aProject in projects:

            project: Project = cast(Project, aProject)

            projectName: ProjectName = ProjectName(project.name)
            projectId:   str         = project.id

            AbstractTodoistStrategy.clsLogger.debug(f'{projectName:12} - {projectId=}')

            projectDictionary[projectName] = project

        return projectDictionary

    def _createProject(self, name: ProjectName) -> Project:

        project: Project = self._todoist.add_project(name=name)
        self.clsLogger.info(f'New project: {project.id}')
        return project

    def _synchronize(self, progressCb):
        # TODO: This method is unneeded
        progressCb('Done')

    def _infoLogCloneInformation(self, info: CloneInformation, progressCb: Callable):

        if AbstractTodoistStrategy.clsLogger.isEnabledFor(INFO) is True:
            AbstractTodoistStrategy.clsLogger.info(f'{progressCb.__name__}')

            AbstractTodoistStrategy.clsLogger.info(f'{info.repositoryTask=} {info.milestoneNameTask=}')
            for t in info.tasksToClone:
                gitIssueInfo: GitIssueInfo = cast(GitIssueInfo, t)
                AbstractTodoistStrategy.clsLogger.info(f'{gitIssueInfo.gitIssueName}')
