
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ALIGN_RIGHT
from wx import ALIGN_TOP
from wx import ALL
from wx import BU_LEFT
from wx import CB_DROPDOWN
from wx import CB_READONLY
from wx import EVT_BUTTON
from wx import EVT_COMBOBOX
from wx import EVT_LISTBOX
from wx import EXPAND
from wx import HORIZONTAL
from wx import ICON_ERROR
from wx import LB_MULTIPLE
from wx import LB_OWNERDRAW
from wx import LB_SINGLE
from wx import OK
from wx import VERTICAL

from wx import Button
from wx import CommandEvent
from wx import StaticBoxSizer
from wx import ListBox
from wx import BoxSizer
from wx import ComboBox
from wx import Window

from wx import NewIdRef as wxNewIdRef

from wx.lib.agw.genericmessagedialog import GenericMessageDialog

from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssue
from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssues
from pygitissue2todoist.adapters.GitHubAdapter import GithubAdapter
from pygitissue2todoist.adapters.GitHubAdapter import RepositoryNames
from pygitissue2todoist.adapters.AdapterAuthenticationError import AdapterAuthenticationError
from pygitissue2todoist.adapters.GitHubConnectionError import GitHubConnectionError

from pygitissue2todoist.general.Preferences import Preferences

from pygitissue2todoist.ui.BasePanel import BasePanel
from pygitissue2todoist.ui.dialogs.configuration.DlgConfigure import DlgConfigure

from pygitissue2todoist.ui.eventengine.Events import EventType
from pygitissue2todoist.ui.eventengine.IEventEngine import IEventEngine


class GitHubPanel(BasePanel):

    ALL_ISSUES_INDICATOR:     str = 'All'
    OPEN_MILESTONE_INDICATOR: str = 'Open'
    OPEN_ISSUE_INDICATOR:     str = 'open'

    def __init__(self, parent: Window, eventEngine: IEventEngine):

        super().__init__(parent)

        self.SetBackgroundColour(self.backgroundColor)

        self.logger: Logger = getLogger(__name__)

        self._eventEngine:             IEventEngine          = eventEngine
        self._preferences:             Preferences           = Preferences()
        self._selectedSimpleGitIssues: AbbreviatedGitIssues  = AbbreviatedGitIssues([])

        self._githubAdapter: GithubAdapter = GithubAdapter(userName=self._preferences.githubUserName, authenticationToken=self._preferences.githubApiToken)

        contentSizer: BoxSizer = self._layoutContent()

        # noinspection PyUnresolvedReferences
        self.SetSizer(contentSizer)
        self.Fit()

    def clearIssues(self):
        self._issueList.Clear()
        self._selectedSimpleGitIssues = AbbreviatedGitIssues([])

    def _layoutContent(self) -> BoxSizer:

        sizer: BoxSizer = BoxSizer(VERTICAL)

        rz: StaticBoxSizer = self._createRepositorySelection()
        mz: StaticBoxSizer = self._createMilestoneSelection()
        iz: StaticBoxSizer = self._createIssueSelection()
        bz: BoxSizer       = self._createCloneButton()

        sizer.Add(rz, BasePanel.PROPORTION_NOT_CHANGEABLE, ALL | EXPAND, 1)
        sizer.Add(mz, BasePanel.PROPORTION_CHANGEABLE, ALL | EXPAND, 2)
        sizer.Add(iz, BasePanel.PROPORTION_CHANGEABLE, ALL | EXPAND | ALIGN_TOP, 1)
        sizer.Add(bz, BasePanel.PROPORTION_NOT_CHANGEABLE, ALL | ALIGN_RIGHT, 2)

        sizer.Fit(self)

        return sizer

    def _createRepositorySelection(self) -> StaticBoxSizer:

        repoSelectionWxId: int = wxNewIdRef()

        self._repositorySelection: ComboBox = ComboBox(self, repoSelectionWxId, style=CB_DROPDOWN | CB_READONLY)

        sz = StaticBoxSizer(VERTICAL, self, "Repository List")
        sz.Add(self._repositorySelection, BasePanel.PROPORTION_NOT_CHANGEABLE, EXPAND)

        self.__populateRepositories()

        self.Bind(EVT_COMBOBOX, self._onRepositorySelected, id=repoSelectionWxId)

        return sz

    def _createMilestoneSelection(self) -> StaticBoxSizer:

        milestoneSelectionWxId: int = wxNewIdRef()

        self._milestoneList: ListBox = ListBox(self,  milestoneSelectionWxId, style=LB_SINGLE | LB_OWNERDRAW)

        # noinspection PyUnresolvedReferences
        self._milestoneList.Enable(False)
        sz = StaticBoxSizer(VERTICAL, self, "Repository Milestone Titles")
        sz.Add(self._milestoneList, BasePanel.PROPORTION_CHANGEABLE, EXPAND)

        self.Bind(EVT_LISTBOX, self._onMilestoneSelected, milestoneSelectionWxId)

        return sz

    def _createIssueSelection(self) -> StaticBoxSizer:

        issueWxID: int = wxNewIdRef()

        self._issueList: ListBox = ListBox(self,  issueWxID, style=LB_MULTIPLE | LB_OWNERDRAW)

        # noinspection PyUnresolvedReferences
        self._issueList.Enable(False)
        sz = StaticBoxSizer(VERTICAL, self, "Repository Issues")
        sz.Add(self._issueList, BasePanel.PROPORTION_CHANGEABLE, EXPAND)

        return sz

    def _createCloneButton(self) -> BoxSizer:

        bSizer:    BoxSizer = BoxSizer(HORIZONTAL)
        cloneWxID: int      = wxNewIdRef()

        self._cloneButton: Button = Button(self, id=cloneWxID, style=BU_LEFT, label='Clone')

        # noinspection PyUnresolvedReferences
        self._cloneButton.Enable(False)
        bSizer.Add(self._cloneButton, BasePanel.PROPORTION_NOT_CHANGEABLE, ALL, 1)

        self.Bind(EVT_BUTTON, self._onCloneClicked, id=cloneWxID)
        return bSizer

    def _onRepositorySelected(self, event: CommandEvent):

        repoName: str = event.GetString()
        self.logger.info(f'{repoName=}')

        self.__populateMilestones(repoName)

        self._eventEngine.sendEvent(eventType=EventType.RepositorySelected)

    def _onMilestoneSelected(self, event: CommandEvent):

        repoName:      str = self._repositorySelection.GetStringSelection()
        milestoneTitle: str = event.GetString()
        self.logger.info(f'{repoName=} - {milestoneTitle=}')

        self.clearIssues()
        self.__populateIssues(repoName=repoName, milestoneTitle=milestoneTitle)
        self._eventEngine.sendEvent(eventType=EventType.MilestoneSelected)

    # noinspection PyUnusedLocal
    def _onCloneClicked(self, event: CommandEvent):

        selectedIndices: List[int] = self._issueList.GetSelections()
        self.logger.info(f'{selectedIndices=}')

        for idx in selectedIndices:
            simpleGitIssue: AbbreviatedGitIssue = self._issueList.GetClientData(idx)
            self._selectedSimpleGitIssues.append(simpleGitIssue)

        self.logger.info(f'{self._selectedSimpleGitIssues=}')

        repositoryName: str = self._repositorySelection.GetStringSelection()
        milestoneName:  str = self._milestoneList.GetStringSelection()

        self._eventEngine.sendEvent(eventType=EventType.IssuesSelected,
                                    repositoryName=repositoryName,
                                    milestoneName=milestoneName,
                                    selectedSimpleGitIssues=self._selectedSimpleGitIssues)

    def __populateRepositories(self):

        try:
            repoNames: RepositoryNames = self._githubAdapter.getRepositoryNames()

            self._repositorySelection.SetItems(repoNames)
        except AdapterAuthenticationError:
            self.__handleAuthenticationError()
        except GitHubConnectionError:
            self.__handleGitHubConnectionError()

    def __populateMilestones(self, repoName: str):

        mileStoneTitles: List[str] = self._githubAdapter.getMileStoneTitles(repoName)

        self._milestoneList.SetItems(mileStoneTitles)
        # noinspection PyUnresolvedReferences
        self._milestoneList.Enable(True)

    def __populateIssues(self, repoName: str, milestoneTitle: str):
        """
        The UI control can only display strings
        Args:
            repoName:       The repository name
            milestoneTitle: The milestone for which we will filter
        """
        abbreviatedGitIssues: AbbreviatedGitIssues = self._githubAdapter.getAbbreviatedIssues(repoName, milestoneTitle)

        for abbreviatedGitIssue in abbreviatedGitIssues:
            simpleGitIssue: AbbreviatedGitIssue = cast(AbbreviatedGitIssue, abbreviatedGitIssue)
            # Insert string in list box;  Attach client data to it
            self._issueList.Append(simpleGitIssue.issueTitle, simpleGitIssue)

        # noinspection PyUnresolvedReferences
        self._issueList.Enable(True)
        # noinspection PyUnresolvedReferences
        self._cloneButton.Enable(True)

    def __extractTitles(self, abbreviatedGitIssues: AbbreviatedGitIssues) -> List[str]:

        issueTitles: List[str] = []
        for simpleGitIssues in abbreviatedGitIssues:
            issueTitles.append(simpleGitIssues.issueTitle)

        return issueTitles

    def __handleAuthenticationError(self):

        eDlg = GenericMessageDialog(None, 'GitHub authentication error', "", agwStyle=ICON_ERROR | OK)
        eDlg.ShowModal()
        eDlg.Destroy()

        with DlgConfigure(self) as dlg:
            if dlg.ShowModal() == OK:
                githubToken: str = self._preferences.githubApiToken
                userName:    str = self._preferences.githubUserName
                self._githubAdapter = GithubAdapter(userName=userName, authenticationToken=githubToken)

                self.__populateRepositories()  # I hate recursion

    def __handleGitHubConnectionError(self):

        eDlg = GenericMessageDialog(None, 'GitHub connection error.  Try again later', "", agwStyle=ICON_ERROR | OK)
        eDlg.ShowModal()
        eDlg.Destroy()
