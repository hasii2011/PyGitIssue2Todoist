
from wx import DefaultSize
from wx import LB_EXTENDED

from wx import ListBox
from wx import Size
from wx import Window

from wx import BeginBusyCursor as wxBeginBusyCursor
from wx import EndBusyCursor as wxEndBusyCursor
from wx import Yield as wxYield
from wx import CallAfter as wxCallAfter

from pygitissue2todoist.adapters.GitHubAdapter import GithubAdapter
from pygitissue2todoist.adapters.GitHubAdapter import Slugs


class RepositorySelector(ListBox):

    def __init__(self, parent: Window, gitHubAdapter: GithubAdapter):

        super().__init__(parent, size=Size(width=-1, height=300), style=LB_EXTENDED)

        self._githubAdapter: GithubAdapter = gitHubAdapter
        wxCallAfter(self._populate)

    def _populate(self):
        wxBeginBusyCursor()
        wxYield()

        slugs: Slugs = self._githubAdapter.getRepositoryNames()
        slugs.sort()
        wxEndBusyCursor()

        self.Set(slugs)
