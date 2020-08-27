
class Version:

    __appName__: str = 'gittodoistclone'
    __version__: str = 'Alpha-0.5'
    __website__: str = 'https://github.com/hasii2011/gittodoistclone/wiki'

    @classmethod
    def applicationName(cls) -> str:
        return cls.__appName__

    @classmethod
    def applicationVersion(cls) -> str:
        return cls.__version__

    @classmethod
    def applicationWebSite(cls) -> str:
        return cls.__website__

