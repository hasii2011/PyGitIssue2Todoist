
from typing import Any
from typing import cast

from wx import DefaultPosition
from wx import DefaultSize
from wx import ID_ANY
from wx import LC_REPORT
from wx import LC_SORT_ASCENDING
from wx import LIST_AUTOSIZE
from wx import ListCtrl
from wx import Window

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssue
from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssues


class IssueSelector(ListCtrl, ListCtrlAutoWidthMixin):

    def __init__(self, parent: Window):

        super().__init__()
        ListCtrl.__init__(self, parent, ID_ANY, pos=DefaultPosition, size=DefaultSize, style=LC_SORT_ASCENDING | LC_REPORT)

        ListCtrlAutoWidthMixin.__init__(self)

        self._issues: AbbreviatedGitIssues = cast(AbbreviatedGitIssues, None)
        self._createHeader()

    def _issueSetter(self, issues: AbbreviatedGitIssues) -> None:
        self._issues = issues

        for issue in issues:
            realIssue: AbbreviatedGitIssue = cast(AbbreviatedGitIssue, issue)

            index = self.InsertItem(self.GetItemCount(), realIssue.slug)
            print(f'{index=}')
            self.SetItem(index, 1, realIssue.issueTitle)
            # self.SetItemData(index, realIssue)

        self.SetColumnWidth(0, LIST_AUTOSIZE)
        self.SetColumnWidth(1, LIST_AUTOSIZE)

    # noinspection PyTypeChecker
    issues = property(fget=cast(Any, None), fset=_issueSetter, doc='Repeated calls append the issues')     # type ignore

    def _createHeader(self):
        self.InsertColumn(0, "Repository")
        self.InsertColumn(1, "Issue")
