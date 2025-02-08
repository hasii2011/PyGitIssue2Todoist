
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger
from logging import INFO

from wx import CB_DROPDOWN
from wx import CB_READONLY
from wx import EVT_BUTTON
from wx import EVT_COMBOBOX
from wx import EVT_LISTBOX
from wx import EVT_RADIOBOX
from wx import ICON_ERROR
from wx import ID_ANY
from wx import LB_MULTIPLE
from wx import LB_OWNERDRAW
from wx import LB_SINGLE
from wx import OK

from wx import Button
from wx import CommandEvent
from wx import ListBox
from wx import ComboBox
from wx import RadioBox

from wx.lib.agw.genericmessagedialog import GenericMessageDialog
from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssue
from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssues
from pygitissue2todoist.adapters.GitHubAdapter import GithubAdapter
from pygitissue2todoist.adapters.GitHubAdapter import RepositoryNames
from pygitissue2todoist.adapters.AdapterAuthenticationError import AdapterAuthenticationError
from pygitissue2todoist.adapters.GitHubConnectionError import GitHubConnectionError

from pygitissue2todoist.general.PreferencesV2 import PreferencesV2

from pygitissue2todoist.ui.BasePanel import BasePanel
from pygitissue2todoist.ui.dialogs.configuration.DlgConfigure import DlgConfigure

from pygitissue2todoist.ui.eventengine.Events import EventType
from pygitissue2todoist.ui.eventengine.IEventEngine import IEventEngine
from pygitissue2todoist.ui.eventengine.Events import EVT_TASK_CREATION_COMPLETE
from pygitissue2todoist.ui.eventengine.Events import TaskCreationCompleteEvent


class GitHubPanel(BasePanel):

    ALL_ISSUES_INDICATOR:     str = 'All'
    OPEN_MILESTONE_INDICATOR: str = 'Open'
    OPEN_ISSUE_INDICATOR:     str = 'open'

    WORKFLOW_SINGLE_REPOSITORY: str = 'Select from single repository'
    WORKFLOW_ALL_ASSIGNED_ISSUES:        str = 'All issues assigned to me'

    def __init__(self, parent: SizedPanel, eventEngine: IEventEngine):

        super().__init__(parent)
        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        self.SetBackgroundColour(self.backgroundColor)

        self.logger: Logger = getLogger(__name__)

        self._eventEngine:             IEventEngine          = eventEngine
        self._preferences:             PreferencesV2         = PreferencesV2()
        self._selectedSimpleGitIssues: AbbreviatedGitIssues  = AbbreviatedGitIssues([])

        self._githubAdapter: GithubAdapter = GithubAdapter(userName=self._preferences.gitHubUserName, authenticationToken=self._preferences.gitHubAPIToken)

        self._workflowList:        RadioBox = cast(RadioBox, None)
        self._repositorySelection: ComboBox = cast(ComboBox, None)
        self._milestoneList:       ListBox  = cast(ListBox, None)
        self._issueList:           ListBox  = cast(ListBox, None)
        self._layoutContent(parent=self)

        self._populateRepositories()

        self.Bind(EVT_COMBOBOX, self._onRepositorySelected, self._repositorySelection)
        self.Bind(EVT_LISTBOX,  self._onMilestoneSelected,  self._milestoneList)
        self.Bind(EVT_BUTTON,   self._onCloneClicked,       self._cloneButton)
        self.Bind(EVT_RADIOBOX,   self._onWorkflowSelected,   self._workflowList)

        self._eventEngine.registerListener(event=EVT_TASK_CREATION_COMPLETE, callback=self._onTaskCreationComplete)

    def clearIssues(self):
        self._issueList.Clear()
        self._selectedSimpleGitIssues = AbbreviatedGitIssues([])

    def _layoutContent(self, parent: BasePanel):

        self._layoutWorkflowChooser(parent=parent)
        self._layoutRepositorySelection(parent=parent)
        self._layoutMilestoneSelection(parent=parent)
        self._layoutIssueSelection(parent=parent)
        self._layoutCloneButton(parent=parent)

        # Set default value from preferences
        # Note that the indices originate from the order of the choices in the RadioBox constructor
        # This step must happen after the layout of all of the componenets to ensure that none of them
        # still have the initial value of `None`
        preferred_single_repo = not self._preferences.assignmentMode
        self._workflowList.SetSelection(0 if preferred_single_repo else 1)
        self._update_UI_on_workflow_type(preferred_single_repo)


    def _layoutWorkflowChooser(self, parent: SizedPanel):

        radio = RadioBox(parent,
                    ID_ANY,
                    "Select GitHub Workflow",
                    choices=[self.WORKFLOW_SINGLE_REPOSITORY, self.WORKFLOW_ALL_ASSIGNED_ISSUES],
                    majorDimension=1
                )

        self._workflowList = radio

    def _onWorkflowSelected(self, event: CommandEvent):

        # First clear the existing issues and tasks lists
        self._eventEngine.sendEvent(eventType=EventType.WorkflowSelected)

        print(f'{event=}')
        print(f'{event.GetString()=}')

        single_repo = event.GetString() == self.WORKFLOW_SINGLE_REPOSITORY
        
        # Set this in the preferences so that it is remembered for subsequent restarts
        self._preferences.assignmentMode = not single_repo

        print(f'{self._workflowList.GetString(self._workflowList.GetSelection())=}')
        self._update_UI_on_workflow_type(single_repo)

    def _update_UI_on_workflow_type(self, single_repo: bool):
        # Enable or disable the repository selection components
        # We need to use `Parent`, as each control is wrapped in a SizedStaticBox
        # and it is the SizedStaticBox that we need to Show/Hide
        self._repositorySelection.Parent.Show(single_repo)
        self._milestoneList.Parent.Show(single_repo)
        self.Layout()
 
        if not single_repo:
            # Now populate the assigned issues
            self._populateAssignedIssues()

    def _layoutRepositorySelection(self, parent: SizedPanel):

        box: SizedStaticBox = SizedStaticBox(parent, ID_ANY, "Repositories")
        box.SetSizerProps(expand=True, proportion=1)

        self._repositorySelection = ComboBox(box, style=CB_DROPDOWN | CB_READONLY)
        self._repositorySelection.SetSizerProps(expand=True)

    def _layoutMilestoneSelection(self, parent: SizedPanel):

        box: SizedStaticBox = SizedStaticBox(parent, ID_ANY, "Repository Milestone Titles")
        box.SetSizerProps(expand=True, proportion=4)

        self._milestoneList = ListBox(box, style=LB_SINGLE | LB_OWNERDRAW)
        self._milestoneList.SetSizerProps(expand=True, proportion=1)

        self._milestoneList.Enable(False)

    def _layoutIssueSelection(self, parent: SizedPanel):

        box: SizedStaticBox = SizedStaticBox(parent, ID_ANY, "Repository Issues")
        box.SetSizerProps(expand=True, proportion=4)

        self._issueList = ListBox(box, style=LB_MULTIPLE | LB_OWNERDRAW)
        self._issueList.SetSizerProps(expand=True, proportion=1)

        self._issueList.Enable(False)

    def _layoutCloneButton(self, parent: SizedPanel):

        sizedPanel: SizedPanel = SizedPanel(parent)
        sizedPanel.SetSizerType('horizontal')
        sizedPanel.SetSizerProps(expand=False, halign='right')  # expand False allows aligning right

        self._cloneButton: Button = Button(sizedPanel, label='Clone')

        self._cloneButton.Enable(False)

    def _onRepositorySelected(self, event: CommandEvent):

        repoName: str = event.GetString()
        self.logger.info(f'{repoName=}')

        self._populateMilestones(repoName)

        self._eventEngine.sendEvent(eventType=EventType.RepositorySelected)

    def _onMilestoneSelected(self, event: CommandEvent):

        repoName:      str = self._repositorySelection.GetStringSelection()
        milestoneTitle: str = event.GetString()
        self.logger.info(f'{repoName=} - {milestoneTitle=}')

        self.clearIssues()
        self._populateIssues(repoName=repoName, milestoneTitle=milestoneTitle)
        self._eventEngine.sendEvent(eventType=EventType.MilestoneSelected)

    # noinspection PyUnusedLocal
    def _onCloneClicked(self, event: CommandEvent):

        selectedIndices: List[int] = self._issueList.GetSelections()
        self.logger.info(f'{selectedIndices=}')

        for idx in selectedIndices:
            simpleGitIssue: AbbreviatedGitIssue = self._issueList.GetClientData(idx)
            self._selectedSimpleGitIssues.append(simpleGitIssue)

        self._infoLogSelectedIssues()

        repositoryName: str = self._repositorySelection.GetStringSelection()
        milestoneName:  str = self._milestoneList.GetStringSelection()

        self._eventEngine.sendEvent(eventType=EventType.IssuesSelected,
                                    repositoryName=repositoryName,
                                    milestoneName=milestoneName,
                                    selectedSimpleGitIssues=self._selectedSimpleGitIssues)

    def _populateRepositories(self):

        try:
            repoNames: RepositoryNames = self._githubAdapter.getRepositoryNames()

            self._repositorySelection.SetItems(repoNames)
        except AdapterAuthenticationError:
            self._handleAuthenticationError()
        except GitHubConnectionError:
            self._handleGitHubConnectionError()

    def _populateMilestones(self, repoName: str):

        mileStoneTitles: List[str] = self._githubAdapter.getMileStoneTitles(repoName)

        self._milestoneList.SetItems(mileStoneTitles)
        self._milestoneList.Enable(True)

    def _populateAssignedIssues(self):
        try:
            abbreviatedGitIssues: AbbreviatedGitIssues = self._githubAdapter.getAssignedToMeIssues()
        except AdapterAuthenticationError:
            self._handleAuthenticationError()
        except GitHubConnectionError:
            self._handleGitHubConnectionError()

        for abbreviatedGitIssue in abbreviatedGitIssues:
            simpleGitIssue: AbbreviatedGitIssue = cast(AbbreviatedGitIssue, abbreviatedGitIssue)
            # Insert string in list box;  Attach client data to it
            # TODO: In would be nice to be able to add some formatting to these strings
            # (eg have the prefix in bold or a different color)
            full_title = f'{simpleGitIssue.prefix} {simpleGitIssue.issueTitle}'
            self._issueList.Append(full_title, simpleGitIssue)

        self._issueList.Enable(True)
        self._cloneButton.Enable(True)

    def _populateIssues(self, repoName: str, milestoneTitle: str):
        """
        The UI control can only display strings
        Args:
            repoName:       The repository name
            milestoneTitle: The milestone for which we will filter
        """

        print(f'{self._workflowList.GetSelection()=}')

        abbreviatedGitIssues: AbbreviatedGitIssues = self._githubAdapter.getAbbreviatedIssues(repoName, milestoneTitle)

        for abbreviatedGitIssue in abbreviatedGitIssues:
            simpleGitIssue: AbbreviatedGitIssue = cast(AbbreviatedGitIssue, abbreviatedGitIssue)
            # Insert string in list box;  Attach client data to it
            self._issueList.Append(simpleGitIssue.issueTitle, simpleGitIssue)

        self._issueList.Enable(True)
        self._cloneButton.Enable(True)

    def _extractTitles(self, abbreviatedGitIssues: AbbreviatedGitIssues) -> List[str]:

        issueTitles: List[str] = []
        for simpleGitIssues in abbreviatedGitIssues:
            issueTitles.append(simpleGitIssues.issueTitle)

        return issueTitles

    def _handleAuthenticationError(self):

        eDlg = GenericMessageDialog(None, 'GitHub authentication error', "", agwStyle=ICON_ERROR | OK)
        eDlg.ShowModal()
        eDlg.Destroy()

        with DlgConfigure(self) as dlg:
            if dlg.ShowModal() == OK:
                githubToken: str = self._preferences.gitHubAPIToken
                userName:    str = self._preferences.gitHubUserName
                self._githubAdapter = GithubAdapter(userName=userName, authenticationToken=githubToken)

                self._populateRepositories()  # I hate recursion

    def _handleGitHubConnectionError(self):

        eDlg = GenericMessageDialog(None, 'GitHub connection error.  Try again later', "", agwStyle=ICON_ERROR | OK)
        eDlg.ShowModal()
        eDlg.Destroy()

    # noinspection PyUnusedLocal
    def _onTaskCreationComplete(self, event: TaskCreationCompleteEvent):
        self.clearIssues()

    def _infoLogSelectedIssues(self):
        if self.logger.isEnabledFor(INFO) is True:
            for s in self._selectedSimpleGitIssues:
                simpleGitIssue: AbbreviatedGitIssue = cast(AbbreviatedGitIssue, s)
                self.logger.info(f'Selected: {simpleGitIssue.issueTitle}')
