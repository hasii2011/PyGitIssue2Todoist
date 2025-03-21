
from typing import Callable

from logging import Logger
from logging import getLogger

from pygitissue2todoist.strategy.TodoistStrategyTypes import CloneInformation

from pygitissue2todoist.general.Preferences import Preferences

from pygitissue2todoist.strategy.ITodoistCreationStrategy import ITodoistCreationStrategy
from pygitissue2todoist.strategy.TodoistCreateByRepository import TodoistCreateByRepository
from pygitissue2todoist.strategy.TodoistCreateSingleProject import TodoistCreateSingleProject
from pygitissue2todoist.strategy.TodoistTaskCreationStrategy import TodoistTaskCreationStrategy


class TodoistCreation:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        preferences: Preferences = Preferences()

        if preferences.taskCreationStrategy == TodoistTaskCreationStrategy.PROJECT_BY_REPOSITORY:
            self._taskCreationStrategy: ITodoistCreationStrategy = TodoistCreateByRepository()
        elif preferences.taskCreationStrategy == TodoistTaskCreationStrategy.SINGLE_TODOIST_PROJECT:
            self._taskCreationStrategy = TodoistCreateSingleProject()
        else:
            assert False, 'Unknown task creation strategy'

    def createTasks(self, info: CloneInformation, progressCb: Callable):
        self._taskCreationStrategy.createTasks(info=info, progressCb=progressCb)
