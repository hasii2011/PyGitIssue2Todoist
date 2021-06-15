
class TaskCreationError(Exception):

    def __init__(self, *args, **kwargs):

        self._message: str = ''

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, msg: str):
        self._message = msg
