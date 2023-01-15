
from pygitissue2todoist.general.exceptions.BaseCreationError import BaseCreationError


class TaskCreationError(BaseCreationError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
