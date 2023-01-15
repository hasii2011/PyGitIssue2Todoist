from pygitissue2todoist.general.exceptions.BaseCreationError import BaseCreationError


class NoteCreationError(BaseCreationError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
