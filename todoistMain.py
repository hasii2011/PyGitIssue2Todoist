
from todoist.api import TodoistAPI

api_token: str = "86e2b16e4f1d1920c556cc5621e6c5ed468c5445"


def addSimpleTask():

    todoist: TodoistAPI = TodoistAPI(api_token)

    todoist.add_item("Item1")

    todoist.sync()
    todoist.commit()


def addTaskToProject():

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


if __name__ == '__main__':
    # addSimpleTask()
    addTaskToProject()
