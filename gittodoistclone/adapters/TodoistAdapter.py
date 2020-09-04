
from typing import List
from typing import Callable

from dataclasses import dataclass
from dataclasses import field

from logging import Logger
from logging import getLogger

from todoist import TodoistAPI
from todoist.models import Item
from todoist.models import Project
from typing import Dict

from gittodoistclone.adapters.AdapterAuthenticationError import AdapterAuthenticationError


@dataclass
class CloneInformation:
    repositoryTask:    str = ''
    milestoneNameTask: str = ''
    tasksToClone:      List[str] = field(default_factory=list)


class TodoistAdapter:

    def __init__(self, apiToken: str):

        self.logger: Logger = getLogger(__name__)

        self._todoist:  TodoistAPI = TodoistAPI(apiToken)

    def createTasks(self, info: CloneInformation, progressCb: Callable):

        self.logger.info(f'{progressCb.__name__} - {info=}')

        todoist: TodoistAPI = self._todoist

        progressCb('Starting')

        justRepoName: str     = info.repositoryTask.split('/')[1]

        project:      Project = todoist.projects.add(justRepoName)

        progressCb(f'Added {justRepoName}')

        milestoneTaskItem: Item = todoist.items.add(info.milestoneNameTask, project_id=project['id'])

        progressCb(f'Added Milestone: {info.milestoneNameTask}')

        tasks: List[str] = info.tasksToClone

        #
        # To create subtasks first create in project then move them to the milestone task
        #
        for task in tasks:
            subTask: Item = todoist.items.add(task, project_id=project['id'])
            subTask.move(parent_id=milestoneTaskItem['id'])

        progressCb('Start Sync')
        response: Dict[str, str] = self._todoist.sync()
        if "error_tag" in response:
            raise AdapterAuthenticationError(response)
        else:
            progressCb('Committing')
            self._todoist.commit()
            progressCb('Done')
