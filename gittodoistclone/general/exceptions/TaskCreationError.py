
class TaskCreationError(Exception):

    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):

        self._message:   str = ''
        self._errorCode: int = -1

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, msg: str):
        self._message = msg

    @property
    def errorCode(self) -> int:
        return self._errorCode

    @errorCode.setter
    def errorCode(self, newValue: int):
        self._errorCode = newValue
