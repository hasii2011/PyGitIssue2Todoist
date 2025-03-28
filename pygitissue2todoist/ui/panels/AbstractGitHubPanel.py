
from typing import cast

from logging import Logger
from logging import getLogger
from logging import INFO

from abc import abstractmethod

from wx import Window

from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssue
from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssues
from pygitissue2todoist.ui.BasePanel import BasePanel


class AbstractGitHubPanel(BasePanel):

    def __init__(self, parent: Window):
        super().__init__(parent=parent)
        self.logger: Logger = getLogger(__name__)

    @abstractmethod
    def clearIssues(self):
        pass

    def _infoLogSelectedIssues(self, selectedIssues: AbbreviatedGitIssues):
        if self.logger.isEnabledFor(INFO) is True:

            for s in selectedIssues:
                simpleGitIssue: AbbreviatedGitIssue = cast(AbbreviatedGitIssue, s)

                self.logger.info(f'Selected: {simpleGitIssue.issueTitle}')
