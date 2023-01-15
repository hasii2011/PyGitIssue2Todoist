
class InvalidPreference(Exception):

    def __init__(self, *args):

        super().__init__(*args)

        self._preferenceName: str = ''

    @property
    def preferenceName(self) -> str:
        return self._preferenceName

    @preferenceName.setter
    def preferenceName(self, newValue: str):
        self._preferenceName = newValue
