from typing import Dict
from typing import List
from typing import cast

from todoist.api import SyncError
from todoist.api import TodoistAPI
from todoist.models import Item
from todoist.models import Project

from pygitissue2todoist.general.Preferences import Preferences

Preferences.determinePreferencesLocation()

# Used for prototyping

def addSimpleTask():
    api_token: str = Preferences().todoistApiToken

    todoist: TodoistAPI = TodoistAPI(api_token)

    todoist.add_item("Item1")

    todoist.sync()
    todoist.commit()


def addTaskToProject():

    api_token: str = Preferences().todoistApiToken

    todoist: TodoistAPI = TodoistAPI(api_token)
    todoist.sync()

    projects = todoist.state['projects']

    projectId = -1
    for project in projects:

        projectName: str = project["name"]
        if projectName == 'Development':
            projectId = project['id']
            print(f'{projectName=} - {projectId=}')
            break

    taskItem = todoist.items.add('I am an external Task', project_id=projectId)
    taskItem.update(priority=1)

    todoist.sync()

    todoist.commit()


def getProjects():

    api_token: str = Preferences().todoistApiToken

    todoist: TodoistAPI = TodoistAPI(api_token)
    todoist.sync()

    projects = todoist.state['projects']

    for project in projects:
        projectName: str = project["name"]
        projectId:   int = project['id']
        print(f'{projectName:12} - {projectId=}')

        try:
            if projectName == 'PyUt':
                todoist.projects.delete(projectId)
                todoist.sync()
                todoist.commit()
        except SyncError as se:
            print(f'{se=}')


def getProjectTasks():

    api_token: str = Preferences().todoistApiToken

    todoist: TodoistAPI = TodoistAPI(api_token)
    todoist.sync()
    projects: List[Project] = todoist.state['projects']

    mockProject: Project = cast(Project, None)
    for project in projects:

        project = cast(Project, project)
        projectName: str = project["name"]
        if projectName == 'MockProject':
            mockProject = project
            break

    mockProjectId: int = mockProject['id']
    print(f'{mockProjectId=}')

    dataItems: Dict[str, Item] = todoist.projects.get_data(project_id=mockProjectId)

    # noinspection PyTypeChecker
    items: List[Item] = dataItems['items']
    for item in items:
        print(f'{item["content"]=}  {item["id"]=} {item["parent_id"]=}')


if __name__ == '__main__':
    # addSimpleTask()
    # addTaskToProject()
    # getProjects()
    getProjectTasks()
