from todoist.api import SyncError
from todoist.api import TodoistAPI

from gittodoistclone.general.Preferences import Preferences

Preferences.determinePreferencesLocation()


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


if __name__ == '__main__':
    # addSimpleTask()
    # addTaskToProject()
    getProjects()
