
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

from pygitissue2todoist.adapters.AbstractTodoistAdapter import AbstractTodoistAdapter
from pygitissue2todoist.adapters.AbstractTodoistAdapter import ProjectDictionary
from pygitissue2todoist.adapters.AbstractTodoistAdapter import ProjectName
from pygitissue2todoist.adapters.AbstractTodoistAdapter import Tasks


from pygitissue2todoist.adapters.ModeAdapter import TaskPurpose, TodoistTaskInfo
from pygitissue2todoist.adapters.TodoistAdapterTypes import CloneInformation, TaskDescription
from pygitissue2todoist.adapters.TodoistAdapterTypes import GitIssueInfo


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


class TodoistAdapterV2(AbstractTodoistAdapter):
    """
    This version of the adapter creates projects for each GitHub repository.  This is
    ideal for users who have purchased a Todoist license which allows unlimited projects
    """

    def __init__(self, apiToken: str):

        super().__init__(apiToken=apiToken)

        self.logger:             Logger            = getLogger(__name__)
        self._todoist:           TodoistAPI        = TodoistAPI(apiToken)
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

        # tasks: List[GitIssueInfo] = info.tasksToClone

        task_infos = [TodoistTaskInfo(gh_issue=ghi, task_purpose=TaskPurpose.Issue) for ghi in info.tasksToClone]

        for task_info in task_infos:
            hierarchy_params : List[TaskDescription] = self._describe_hierarchy(task_info, info)

            # Now we have all the parameters, we can ensure/create the Project and the hierarchy of tasks
            # The last item in the list is the root task
            root_params = hierarchy_params.pop()

            # Create the root task first:
            # TODO: Is there ever a case where `projectDictionary!=self._getCurrentProjects()`. Could we just make this a default parameter? 
            project_id = self._getProjectId(projectName=ProjectName(root_params.content), projectDictionary=self._getCurrentProjects())

            # Now go through the remaining hierarchy in reverse order
            all_project_tasks = self._todoist.get_tasks(project_id=project_id)
            parent_id = None

            for params in reversed(hierarchy_params):
                # Check if the task already exists
                # We are assume that the task title (content) is unique
                print(f'{params=}')
                if any(task.content == params.content for task in all_project_tasks):
                    # Task already exists, so we don't need to create it
                    # We need to find the task ID
                    parent_id = [task.id for task in all_project_tasks if task.content == params.content][0]
                else:
                    new_task = self._todoist.add_task(
                        project_id=project_id,
                        parent_id=parent_id,
                        content=params.content,
                        description=params.description,
                    )

                    if params.comment:
                        self._todoist.add_comment(task_id=new_task.id, content=params.comment)

                    parent_id = new_task.id

        self._synchronize(progressCb)

    

    def _describe_hierarchy(self, task_info: TodoistTaskInfo, clone_info: CloneInformation):
        """
        Described the hierarchy of parents required for the Github Issue in task_info,


        exists in Todoist. If the tasks do not already exist, they will be created.
        If they do not exist this method will not update them but pass silently.

        The hierarchy will be determined by mode (e.g. single project or multiple projects and milestone-oriented or assigned-issues)

        Args:
            task_info:       The task to create
            clone_info:  The information about the task
            progressCb:     The callback to report status
        """
        # We need to determine all parts of the hierarchy first
        # working up from the bottom
        # If we need to create any part of the hierarchy, it must
        # be created from the top down.

        # This lists the parameters for the tasks, however not all
        # values are known at this point
        draft_params: List[TaskDescription] = []

        milestone_name = clone_info.milestoneNameTask
        repo_name = task_info.gh_issue.github_repo_name
        gh_org_name = task_info.gh_issue.github_org_name

        print(f'{task_info._mode=}')
        print(f'{task_info.get_hierarchy=}')

        for level in task_info.get_hierarchy:
            if level == task_info.get_hierarchy[-1]:
                # This is the root task
                # We need to find the Project ID
                project_id = "SOME PROJECT ID"

            match level:
                case TaskPurpose.Milestone:
                    draft_params.append(
                        TaskDescription(
                            content=milestone_name,
                            description="Milestone task"
                        )
                    )

                case TaskPurpose.Repo:
                    # Get the repo details
                    draft_params.append(
                        TaskDescription(
                            content=repo_name,
                            description="Repo task"
                        )
                    )

                case TaskPurpose.GH_Org:
                    # Get the org details
                    draft_params.append(
                        TaskDescription(
                            content=gh_org_name,
                            description="GitHub Organisation"
                        )
                    )

                case TaskPurpose.NamedProject:
                    # Get the project details
                    root_project_name = self._preferences.todoistProjectName

                    draft_params.append(
                        TaskDescription(
                            content=root_project_name,
                            description="Development project"
                        )
                    )

                case TaskPurpose.Issue:
                    content, description, comment = task_info.gh_issue.format_add_task_params()

                    draft_params.append(
                        TaskDescription(
                            content=content,
                            description=description,
                            comment=comment
                        )
                    )

                case None:
                    raise ValueError("No parent task type found")

        return draft_params


    def _find_subtask_from_parent(self, project_id: str, parent_id: str) -> Tasks:
        """

        Args:
            project_id:  The id of the parent task where all GitHub tasks reside
            parent_id:    The milestone task id

        Returns:
            The list of subtasks that are leaf tasks end of the projectId->repoTaskId->milestoneId task branch
        """
        all_tasks = self._todoist.get_tasks(project_id=project_id)
        sub_task = [task for task in all_tasks if task.parent_id == parent_id]

        return Tasks(sub_task)


    def _determineProjectIdFromRepoName(self, info: CloneInformation, progressCb: Callable) -> str:
        return "SOME PROJECT ID"

    # def _determineProjectIdFromRepoName(self, info: CloneInformation, progressCb: Callable) -> str:
    #     """
    #     Implement empty method from parent;
    #     Gets a project ID from the repo name

    #     Args:
    #         info:  The cloned information
    #         progressCb: A progress callback to return status

    #     Returns:  An appropriate parent ID for newly created tasks
    #     """

    #     try:
    #         self._projectDictionary = self._getCurrentProjects()

    #         justRepoName: str = info.repositoryTask.split('/')[1]
    #         # justRepoName: str = info.
    #         projectId:    str = self._getProjectId(projectName=ProjectName(justRepoName), projectDictionary=self._projectDictionary)

    #         progressCb(f'Added {justRepoName}')

    #         return projectId
    #     except Exception as e:
    #         self.logger.error(f'Error: {e}')

    #         print(f'Error: {e}')
    #         print(f'info: {info}')
    #         raise

    # def _getMilestoneTaskItem(self, projectId: str, milestoneName: str, progressCb: Callable) -> Task:
    #     """
    #     Has the side effect that it sets self._devTasks

    #     Args:
    #         projectId:      The project to search under
    #         milestoneName:  The name of the milestone task
    #         progressCb:     The callback to report status to

    #     Returns:  Either an existing milestone task or a newly created one
    #     """
    #     todoist: TodoistAPI = self._todoist
    #     projectTasks   = self._getProjectTaskItems(projectId=projectId)
    #     self._devTasks = projectTasks.devTasks

    #     milestoneTask:  Task  = cast(Task, None)
    #     mileStoneTasks: Tasks = projectTasks.mileStoneTasks
    #     for task in mileStoneTasks:
    #         self.logger.debug(f'MileStone Task: {task.content=}')
    #         if task.content == milestoneName:
    #             milestoneTask = task
    #             progressCb(f'Found existing milestone: {milestoneName}')
    #             break
    #     # if none found create new one
    #     if milestoneTask is None:
    #         # milestoneTaskItem = todoist.items.add(milestoneNameTask, project_id=projectId)
    #         milestoneTask = todoist.add_task(project_id=projectId, content=milestoneName)
    #         msg: str = f'Added milestone: {milestoneTask}'
    #         progressCb(msg)
    #         self.logger.info(msg)

    #     return milestoneTask

    # def _getProjectTaskItems(self, projectId: str) -> ProjectTasks:
    #     """

    #     Args:
    #         projectId:  The project ID from which we need its task lists or an id
    #         of a parent task

    #     Returns: A class with two lists;  The first are the milestone tasks;  The second are
    #     potential child tasks whose parents are one of the milestone tasks
    #     """

    #     todoist:   TodoistAPI  = self._todoist

    #     # TODO:  Get tasks associated with the project
    #     tasks: List[Task] = todoist.get_tasks(project_id=projectId)
    #     mileStoneTasks: Tasks = Tasks([])
    #     devTasks:       Tasks = Tasks([])

    #     try:
    #         for item in tasks:
    #             task: Task = cast(Task, item)
    #             parentId: str = task.parent_id  # type: ignore
    #             self.logger.debug(f'{task.content=}  {task.id=} {parentId=}')

    #             if parentId is None:
    #                 mileStoneTasks.append(item)
    #             else:
    #                 devTasks.append(item)
    #     except KeyError:
    #         self.logger.warning('No items means this is a new project')

    #     projectTasks: ProjectTasks = ProjectTasks(mileStoneTasks=mileStoneTasks, devTasks=devTasks)

    #     return projectTasks
