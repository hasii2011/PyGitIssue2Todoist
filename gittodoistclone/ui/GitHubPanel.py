
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
from wx import PostEvent

from wx import NewIdRef as wxNewIdRef

from wx.lib.agw.genericmessagedialog import GenericMessageDialog

from gittodoistclone.adapters.GithubAdapter import GithubAdapter
from gittodoistclone.adapters.GithubAdapter import RepositoryNames
from gittodoistclone.adapters.AdapterAuthenticationError import AdapterAuthenticationError

from gittodoistclone.general.Preferences import Preferences

from gittodoistclone.ui.CustomEvents import IssuesSelectedEvent
from gittodoistclone.ui.CustomEvents import RepositorySelectedEvent

from gittodoistclone.ui.BasePanel import BasePanel
from gittodoistclone.ui.dialogs.DlgConfigure import DlgConfigure


class GitHubPanel(BasePanel):

    ALL_ISSUES_INDICATOR:     str = 'All'
    OPEN_MILESTONE_INDICATOR: str = 'Open'
    OPEN_ISSUE_INDICATOR:     str = 'open'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.SetBackgroundColour(self.backgroundColor)

        self.logger:      Logger       = getLogger(__name__)

        preferences: Preferences = Preferences()
        self._preferences: Preferences = preferences
        self._selectedIssueNames: List[str] = []

        self._githubAdapter: GithubAdapter = GithubAdapter(userName=preferences.githubUserName, authenticationToken=preferences.githubApiToken)

        contentSizer: BoxSizer = self._layoutContent()

        self.SetSizer(contentSizer)
        self.Fit()

    def selectedIssueNames(self) -> List[str]:
        return self._selectedIssueNames

    def clearIssues(self):
        self._issueList.Clear()

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

        self._milestoneList.Enable(False)
        sz = StaticBoxSizer(VERTICAL, self, "Repository Milestone Titles")
        sz.Add(self._milestoneList, BasePanel.PROPORTION_CHANGEABLE, EXPAND)

        self.Bind(EVT_LISTBOX, self._onMilestoneSelected, milestoneSelectionWxId)

        return sz

    def _createIssueSelection(self) -> StaticBoxSizer:

        issueWxID: int = wxNewIdRef()

        self._issueList: ListBox = ListBox(self,  issueWxID, style=LB_MULTIPLE | LB_OWNERDRAW)

        self._issueList.Enable(False)
        sz = StaticBoxSizer(VERTICAL, self, "Repository Issues")
        sz.Add(self._issueList, BasePanel.PROPORTION_CHANGEABLE, EXPAND)

        return sz

    def _createCloneButton(self) -> BoxSizer:

        bSizer:    BoxSizer = BoxSizer(HORIZONTAL)
        cloneWxID: int      = wxNewIdRef()

        self._cloneButton: Button = Button(self, id=cloneWxID, style=BU_LEFT, label='Clone')

        self._cloneButton.Enable(False)
        bSizer.Add(self._cloneButton, BasePanel.PROPORTION_NOT_CHANGEABLE, ALL, 1)

        self.Bind(EVT_BUTTON, self._onCloneClicked, id=cloneWxID)
        return bSizer

    def _onRepositorySelected(self, event: CommandEvent):

        repoName: str = event.GetString()
        self.logger.info(f'{repoName=}')

        self.__populateMilestones(repoName)

        evt: RepositorySelectedEvent = RepositorySelectedEvent()

        parent = self.GetParent()
        PostEvent(parent, evt)

    def _onMilestoneSelected(self, event: CommandEvent):

        repoName:      str = self._repositorySelection.GetStringSelection()
        milestoneTitle: str = event.GetString()
        self.logger.info(f'{repoName=} - {milestoneTitle=}')

        self.__populateIssues(repoName=repoName, milestoneTitle=milestoneTitle)

    # noinspection PyUnusedLocal
    def _onCloneClicked(self, event: CommandEvent):

        selectedIndices: List[int] = self._issueList.GetSelections()
        self.logger.info(f'{selectedIndices=}')

        for idx in selectedIndices:
            self._selectedIssueNames.append(self._issueList.GetString(idx))

        self.logger.info(f'{self._selectedIssueNames=}')

        repositoryName: str = self._repositorySelection.GetStringSelection()
        milestoneName:  str = self._milestoneList.GetStringSelection()
        evt: IssuesSelectedEvent = IssuesSelectedEvent(repositoryName=repositoryName,
                                                       milestoneName=milestoneName,
                                                       selectedIssues=self._selectedIssueNames)
        parent = self.GetParent()
        PostEvent(parent, evt)

    def __populateRepositories(self):

        try:
            repoNames: RepositoryNames = self._githubAdapter.getRepositoryNames()

            self._repositorySelection.SetItems(repoNames)
        except AdapterAuthenticationError:
            self.__handleAuthenticationError()

    def __populateMilestones(self, repoName: str):

        mileStoneTitles: List[str] = self._githubAdapter.getMileStoneTitles(repoName)

        self._milestoneList.SetItems(mileStoneTitles)
        self._milestoneList.Enable(True)

    def __populateIssues(self, repoName: str, milestoneTitle: str):

        issueTitles: List[str] = self._githubAdapter.getIssueTitles(repoName, milestoneTitle)

        self._issueList.SetItems(issueTitles)
        self._issueList.Enable(True)
        self._cloneButton.Enable(True)

    def __handleAuthenticationError(self):

        eDlg = GenericMessageDialog(self, 'Github authentication error', "", agwStyle=ICON_ERROR | OK)
        eDlg.ShowModal()
        eDlg.Destroy()

        with DlgConfigure(self) as dlg:
            dlg: DlgConfigure = cast(DlgConfigure, dlg)
            if dlg.ShowModal() == OK:
                githubToken: str = self._preferences.githubApiToken
                userName:    str = self._preferences.githubUserName
                self._githubAdapter = GithubAdapter(userName=userName, authenticationToken=githubToken)

                self.__populateRepositories()  # I hate recursion
