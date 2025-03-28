
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from wx import CENTRE
from wx import EVT_BUTTON
from wx import EVT_LISTBOX
from wx import EVT_LIST_ITEM_SELECTED
from wx import ICON_WARNING
from wx import ID_ANY
from wx import OK
from wx import PD_ELAPSED_TIME

from wx import Button
from wx import CommandEvent
from wx import Point
from wx import ProgressDialog
from wx import MessageBox

from codeallybasic.Position import Position

from wx import Yield as wxYield

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssues
from pygitissue2todoist.adapters.GitHubAdapter import GithubAdapter
from pygitissue2todoist.adapters.GitHubAdapter import IssueOwner
from pygitissue2todoist.adapters.GitHubAdapter import Slugs

from pygitissue2todoist.general.Preferences import Preferences

from pygitissue2todoist.ui.BasePanel import BasePanel
from pygitissue2todoist.ui.eventengine.Events import EventType

from pygitissue2todoist.ui.eventengine.IEventEngine import IEventEngine
from pygitissue2todoist.ui.panels.AbstractGitHubPanel import AbstractGitHubPanel
from pygitissue2todoist.ui.panels.IssueSelector import IssueSelector
from pygitissue2todoist.ui.panels.RepositorySelector import RepositorySelector


SELECT_ITEM:   int = 1
DESELECT_ITEM: int = 0

RepositoryName  = NewType('RepositoryName',  str)
RepositoryNames = NewType('RepositoryNames', List[str])


class OwnerIssuesGitHubPanel(AbstractGitHubPanel):
    """
    This is a complicated components.  I tried creating "panels" for each of the selectors
    but I could not get them to size correctly.  Therefore, I instantiated each of the selectors
    and their associated button panels directly inside of the "GitHubPanel".

    This yielded better visual and resizing results.

                                                    --------------------------
                                                    | OwnerIssuesGitHubPanel |
                     -------------------------------|------------------------|------------------------
                     |                              |------------------------|                       |
                     |                              --------------------------                       |
                     |                                  |               |                            |
                     |                                  |               |                            |
            ----------------------          ---------------------       -----------------   ----------------
            | RepositorySelector |          | RepositoryButtons |       | IssueSelector |   | IssueButtons |
            |--------------------|          |-------------------|       |---------------|   |--------------|
            |--------------------|          |-------------------|       |---------------|   |--------------|
            ----------------------          ---------------------       -----------------   ----------------


    """
    def __init__(self, parent: SizedPanel, eventEngine: IEventEngine):

        super().__init__(parent=parent)

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent)
        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1, border=('all', 0))

        self.SetBackgroundColour(self.backgroundColor)

        self._eventEngine: IEventEngine = eventEngine
        self._preferences: Preferences  = Preferences()

        self._selectedSimpleGitIssues: AbbreviatedGitIssues = AbbreviatedGitIssues([])
        self._githubAdapter:           GithubAdapter        = GithubAdapter(userName=self._preferences.gitHubUserName,
                                                                            authenticationToken=self._preferences.gitHubAPIToken
                                                                            )

        self._repositorySelector:        RepositorySelector = cast(RepositorySelector, None)
        self._selectAllReposButton:      Button             = cast(Button, None)
        self._retrieveReposIssuesButton: Button             = cast(Button, None)

        self._issueSelector:         IssueSelector = cast(IssueSelector, None)
        self._selectAllIssuesButton: Button        = cast(Button, None)
        self._cloneButton:           Button        = cast(Button, None)

        self._progressDlg:           ProgressDialog = cast(ProgressDialog, None)

        self._layoutContent(parent=self)
        self._bindEventHandlers()

    def clearIssues(self):
        # self._issueSelector.ClearAll()
        # TODO
        pass

    def _layoutContent(self, parent: BasePanel):

        self._layoutRepositorySelection(parent=parent)
        self._layoutRepositoryButtons(parent=parent)

        self._layoutIssueSelector(parent=parent)
        self._layoutIssueButtons(parent=parent)

        # self._repositorySelectorPanel = RepositorySelectorPanel(parent=parent, gitHubAdapter=self._githubAdapter, eventEngine=self._eventEngine)
        # self._issueSelectorPanel      = IssueSelectorPanel(parent=parent, gitHubAdapter=self._githubAdapter, eventEngine=self._eventEngine)

    def _bindEventHandlers(self):

        self.Bind(EVT_BUTTON, self._onSelectAllRepositories,         self._selectAllReposButton)
        self.Bind(EVT_BUTTON, self._onRetrieveIssuesForRepositories, self._retrieveReposIssuesButton)
        self.Bind(EVT_BUTTON, self._onSelectAllIssues,               self._selectAllIssuesButton)
        self.Bind(EVT_BUTTON, self._onCloneClicked,                  self._cloneButton)

        self.Bind(EVT_LISTBOX,            self._onRepositorySelected, self._repositorySelector)
        self.Bind(EVT_LIST_ITEM_SELECTED, self._onIssueSelected,      self._issueSelector)

    # noinspection PyUnusedLocal
    def _onRetrieveIssuesForRepositories(self, event: CommandEvent):

        selectedRepositories: List[int] = self._repositorySelector.GetSelections()

        if len(selectedRepositories) == 0:
            # This never happens because of _onRepositorySelected()
            MessageBox("No repositories selected", "Select at least one", OK | ICON_WARNING | CENTRE)
        else:
            repositoryNames: RepositoryNames = RepositoryNames([])
            for idx in selectedRepositories:
                name: str = self._repositorySelector.GetString(idx)
                repositoryNames.append(RepositoryName(name))

            self._populateIssueSelector(repositoryNames=repositoryNames)

    def _populateIssueSelector(self, repositoryNames: RepositoryNames):

        self.logger.debug(f'{repositoryNames}')

        self._setupProgressDialog()

        issueOwner: IssueOwner = IssueOwner(self._preferences.gitHubUserName)
        slugs:      Slugs      = self._toSlugs(repositoryNames=repositoryNames)

        issues: AbbreviatedGitIssues = self._githubAdapter.getIssuesAssignedToOwner(slugs=slugs, issueOwner=issueOwner, callback=self._updateDialog)

        self._progressDlg.Destroy()
        self._issueSelector.issues = issues

    # noinspection PyUnusedLocal
    def _onSelectAllRepositories(self, event: CommandEvent):

        itemCount: int = self._repositorySelector.GetCount()
        for idx in range(itemCount):
            self._repositorySelector.Select(idx)

        self._retrieveReposIssuesButton.Enable(True)

    # noinspection PyUnusedLocal
    def _onSelectAllIssues(self, event: CommandEvent):

        itemCount: int = self._issueSelector.GetItemCount()

        for idx in range(itemCount):
            self._issueSelector.Select(idx, on=SELECT_ITEM)

    # noinspection PyUnusedLocal
    def _onRepositorySelected(self, event: CommandEvent):
        """
        A single repository or many may be selected
        Args:
            event:
        """

        if len(self._repositorySelector.GetSelections()) == 0:
            self._retrieveReposIssuesButton.Enable(False)
        else:
            self._retrieveReposIssuesButton.Enable(True)

    # noinspection PyUnusedLocal
    def _onIssueSelected(self, event: CommandEvent):
        self._cloneButton.Enable(True)

    # noinspection PyUnusedLocal
    def _onCloneClicked(self, event: CommandEvent):

        selectedIssues: AbbreviatedGitIssues = self._issueSelector.selectedIssues

        self._infoLogSelectedIssues(selectedIssues)
        self._eventEngine.sendEvent(eventType=EventType.IssuesSelected,
                                    repositoryName='Repository not used',
                                    milestoneName='Milestone not used',
                                    selectedSimpleGitIssues=selectedIssues)

    def _setupProgressDialog(self) -> ProgressDialog:

        self._progressDlg = ProgressDialog("Retrieve Issues", "Hello", style=PD_ELAPSED_TIME)

        position: Position = self._preferences.progressDialogPosition
        self._progressDlg.SetPosition(pt=Point(x=position.x, y=position.y))

        return self._progressDlg

    def _updateDialog(self, newMsg: str):

        self._progressDlg.Pulse(newMsg)
        wxYield()

    def _toSlugs(self, repositoryNames: RepositoryNames) -> Slugs:
        """
        Only works because both are just strings
        Args:
            repositoryNames:

        Returns: Slugs

        """
        return cast(Slugs, repositoryNames)

    def _layoutRepositorySelection(self, parent: SizedPanel):

        box: SizedStaticBox = SizedStaticBox(parent, ID_ANY, "Repositories")
        box.SetSizerProps(expand=True, proportion=1)

        repositorySelector: RepositorySelector = RepositorySelector(parent=box, gitHubAdapter=self._githubAdapter)

        # noinspection PyUnresolvedReferences
        repositorySelector.SetSizerProps(expand=True, proportion=1)

        self._repositorySelector = repositorySelector

    def _layoutRepositoryButtons(self, parent: SizedPanel):

        buttonPanel: SizedPanel = SizedPanel(parent)

        buttonPanel.SetSizerType('horizontal')
        # noinspection PyUnresolvedReferences
        buttonPanel.SetSizerProps(expand=False, halign='right')  # expand False allows aligning right

        selectAllButton:      Button = Button(parent=buttonPanel, id=ID_ANY, label='Select All')
        retrieveIssuesButton: Button = Button(parent=buttonPanel, id=ID_ANY, label='Retrieve Issues')

        retrieveIssuesButton.Enable(False)

        self._selectAllReposButton  = selectAllButton
        self._retrieveReposIssuesButton = retrieveIssuesButton

    def _layoutIssueSelector(self, parent: SizedPanel):

        box: SizedStaticBox = SizedStaticBox(parent, ID_ANY, "Issues")
        box.SetSizerProps(expand=True, proportion=1)

        issueSelector: IssueSelector = IssueSelector(parent=box)
        # noinspection PyUnresolvedReferences
        issueSelector.SetSizerProps(expand=True, proportion=1)

        self._issueSelector = issueSelector

    def _layoutIssueButtons(self, parent: SizedPanel):

        buttonPanel: SizedPanel = SizedPanel(parent)

        buttonPanel.SetSizerType('horizontal')
        # noinspection PyUnresolvedReferences
        buttonPanel.SetSizerProps(expand=False, halign='right')  # expand False allows aligning right

        selectAllButton: Button = Button(parent=buttonPanel, id=ID_ANY, label='Select All')
        cloneButton:     Button = Button(parent=buttonPanel, id=ID_ANY, label='Clone')

        cloneButton.Enable(False)

        self._selectAllIssuesButton = selectAllButton
        self._cloneButton           = cloneButton
