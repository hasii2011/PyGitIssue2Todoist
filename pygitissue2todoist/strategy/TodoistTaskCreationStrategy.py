
from enum import Enum


class TodoistTaskCreationStrategy(Enum):

    SINGLE_TODOIST_PROJECT      = 'Single Todoist Project'
    PROJECT_BY_REPOSITORY       = 'Project by Repository'
    ALL_ISSUES_ASSIGNED_TO_USER = 'All Issues Assigned to User'
    NOT_SET                     = 'Not Set'
