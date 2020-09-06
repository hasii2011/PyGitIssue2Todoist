
class Version:

    __appName__: str = 'gittodoistclone'
    __version__: str = '0.9-Beta'

    __longVersion__: str = "Humberto's Early Beta Version"

    __website__: str = 'https://github.com/hasii2011/gittodoistclone/wiki'

    @classmethod
    def applicationName(cls) -> str:
        return cls.__appName__

    @classmethod
    def applicationVersion(cls) -> str:
        return cls.__version__

    @classmethod
    def applicationLongVersion(cls) -> str:
        return cls.__longVersion__

    @classmethod
    def applicationWebSite(cls) -> str:
        return cls.__website__

