
from typing import Any
from typing import Dict
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from wx import DefaultPosition
from wx import DefaultSize
from wx import ID_ANY
from wx import LC_REPORT
from wx import LIST_AUTOSIZE
from wx import ListCtrl
from wx import ListItem
from wx import Window

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssue
from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssues

NO_ITEM: int = -1       # Syntactic sugar for wxPython

IssueMap = NewType('IssueMap', Dict[int, AbbreviatedGitIssue])


class IssueSelector(ListCtrl, ListCtrlAutoWidthMixin):
    """
    We have to create an Issue map in order to indirectly associate
    item data with the items in the list control.  How silly
    """
    def __init__(self, parent: Window):

        super().__init__()
        ListCtrl.__init__(self, parent, ID_ANY, pos=DefaultPosition, size=DefaultSize, style=LC_REPORT)

        ListCtrlAutoWidthMixin.__init__(self)

        self.logger:  Logger = getLogger(__name__)
        self._issues: AbbreviatedGitIssues = cast(AbbreviatedGitIssues, None)

        self._issueMap: IssueMap = IssueMap({})

        self._createHeader()

    @property
    def selectedIssues(self) -> AbbreviatedGitIssues:
        """
        A wrapper around the complex logic needed to get the issues
        associated with the items that are displayed

        Returns:  The selected data
        """

        selectedIssues: AbbreviatedGitIssues = AbbreviatedGitIssues([])

        idx:  int      = self.GetFirstSelected()
        issue: AbbreviatedGitIssue = self._issueMap[idx]
        selectedIssues.append(issue)

        while True:
            idx  = self.GetNextSelected(idx)
            if idx == NO_ITEM:
                break

            issue = self._issueMap[idx]
            selectedIssues.append(issue)

        return selectedIssues

    def _issueSetter(self, issues: AbbreviatedGitIssues) -> None:
        """
        Updates the UI.  Using the index in the control as the key to the issue map

        Args:
            issues:

        """
        self._issues = issues

        if self.GetItemCount() > 0:
            self.ClearAll()
            self._issueMap = IssueMap({})

        for issue in issues:
            realIssue: AbbreviatedGitIssue = cast(AbbreviatedGitIssue, issue)

            index = self.InsertItem(self.GetItemCount(), realIssue.slug)
            self.logger.debug(f'{index=}')
            self.SetItem(index=index, column=1, label=realIssue.issueTitle)
            item: ListItem = self.GetItem(index)

            item.SetData(index)
            self._issueMap[index] = realIssue

        self.SetColumnWidth(0, LIST_AUTOSIZE)
        self.SetColumnWidth(1, LIST_AUTOSIZE)

    # noinspection PyTypeChecker
    issues = property(fget=cast(Any, None), fset=_issueSetter, doc='Repeated calls append the issues')     # type ignore

    def _createHeader(self):
        self.InsertColumn(0, "Repository")
        self.InsertColumn(1, "Issue")
