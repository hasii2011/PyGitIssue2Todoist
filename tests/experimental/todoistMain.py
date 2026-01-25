
from typing import Iterator
from typing import cast

from github.Project import Project

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

from pygitissue2todoist.general.Preferences import Preferences


MOCK_PROJECT_NAME: str = 'MockProject'
# Used for prototyping


def addSimpleTask():
    api_token: str = Preferences().todoistAPIToken

    todoist: TodoistAPI = TodoistAPI(api_token)

    try:
        task: Task = todoist.add_task(
            content="Buy Milk",
            due_string="tomorrow at 12:00",
            due_lang="en",
            priority=4,
        )
        print(task)
    except Exception as error:
        print(error)


def addTaskToProject():

    api_token: str = Preferences().todoistAPIToken

    todoist: TodoistAPI = TodoistAPI(api_token)
    projectIter: Iterator = todoist.get_projects()     # type: ignore
    # projects: List[Project] = todoist.get_projects()     # type: ignore

    mockProject: Project = cast(Project, None)
    for projects in projectIter:
        for p in projects:
            project: Project = p
            if project.name == MOCK_PROJECT_NAME:
                mockProject = project
                break
    assert mockProject is not None, "I need a ring to hang my hat on"

    try:
        task: Task = todoist.add_task(project_id=mockProject.id, content='MockTaskOnProject')   # type: ignore
        print(task)
    except Exception as error:
        print(error)


def getProjects():

    api_token: str = Preferences().todoistAPIToken

    todoist: TodoistAPI = TodoistAPI(api_token)

    projectIter: Iterator = todoist.get_projects()     # type: ignore
    for projects in projectIter:
        for p in projects:
            project: Project = p

            print(f'{project.name:15} - {project.id=}')


def getProjectTasks():

    api_token: str = Preferences().todoistAPIToken

    todoist:  TodoistAPI    = TodoistAPI(api_token)
    # projects: List[Project] = todoist.get_projects()     # type: ignore
    projectsIter: Iterator = todoist.get_projects()

    mockProject: Project = cast(Project, None)
    for projects in projectsIter:
        for p in projects:

            project: Project = p

            if project.name == MOCK_PROJECT_NAME:
                mockProject = project
                break

    print(f'{mockProject.id=}')

    taskIter: Iterator = todoist.get_tasks(project_id=mockProject.id)   # type: ignore
    # tasks: List[Task] = todoist.get_tasks(project_id=mockProject.id)

    for tasks in taskIter:
        for t in tasks:
            task: Task = t
            print(f'{task.content:15}  {task.id=} {task.parent_id=}')


if __name__ == '__main__':
    # addSimpleTask()
    addTaskToProject()
    # getProjects()
    # getProjectTasks()
