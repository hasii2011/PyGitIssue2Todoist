# About this doc

This doc contains incomplete, rolling notes during development of this PR. The intention is that this will be the draft of the message that will be included in the PR once it is ready to be submitted.

# Intro

Thank you for this handy tool.

I've been working on a new feature that helps me and might be of use to others. My work tends to be spread across multiple repos and GitHub organisations, and I wanted to adapt PyGitIssue2Todoist to reflect this way of working.

I've open this PR in draft mode to ask for your opinions - I've not finished work on it yet. Are you still actively working on this repo? Are you happy to take contributions or would you would prefer I keep my changes in a fork?


# About the PR

This PR attempt to provide a new workflow for the GitHub to Todoist sync. This mode is based on the "Assigned to me" search option within the GitHub API and CLI. The aim is to help users who are working on multiple projects (and possibly multiple organisation), and want to see all of *their own* tasks in one place.


# About the Todoist Adapter

The structure of Issue -> Milestone -> Repository -> Project is quite deeply integrated into the current implementation of the TodoistAdapter (including the AbstractTodoistAdapter). Initially I attempted to create a new TodoistAdapterAssigned that inherited from AbstractTodoistAdapter. However I could not find an elegant way to avoid the implied hierarchy. Replacing the word "milestone" in with "parent" was insufficient, as that still left implied hierarchy as exactly three levels deep.

Instead I attempted to create the hierarchy as a data structure that was passed to the TodoistAdapter. The relevant hierarchy is selected based on the mode, and then created dynamically.

I have not yet tested this exhaustively, but should offer a more flexible way to defined the hierarchy. It should be possible to offer the users more options about how they want to structure their tasks in Todoist, without new option needing to major changes to the code.

This approach removes the need for there to be multiple subclasses of TodoistAdapter. Therefore this PR also removes the `TodoistAdapterSingleProject` class. I believe that it also removes the need for separating the `TodoistAdapter` and `AbstractTodoistAdapter` classes, but I have not yet merged these two classes.


# Matching the GitHub Issues to the Todoist Tasks hierarchy

Always start with GitHub Issues as the nodes of the hierarchy, with order 0. These are constant across all modes, whereas the other parts of the hierarchy are vary with mode.

## Existing options

### Standard Mode

| Order   | GitHub | Todoist |
|--------|---------|--|
| 0 | Issue | Subtask |
| 1  | Milestone | Top Level Task |
| 2 | Repository | Project - Name from Repo |

### Single Project Mode

| Order   | GitHub | Todoist |
|--------|---------|--|
| 0 | Issue | Sub-Subtask |
| 1  | Milestone | SubTask |
| 2 | Repository | Top Level Task |
| 3 | n/a | Single Project - name from config |

## New Option

### Single Project Assigned to me Mode

| Order   | GitHub | Todoist |
|--------|---------|--|
| 0 | GH Issue | Sub-Subtask |
| 1 | GH Repo | Subtask |
| 2  | GH Org | Top Level Task |
| 3 | n/a | Single Project - name from config |


### Multiple Projects Assigned to me Mode

**NOT YET IMPLEMENTED/TESTED**

| Order   | GitHub | Todoist |
|--------|---------|--|
| 0 | GH Issue | Subtask |
| 1 | GH Repo | Top Level task |
| 2  | GH Org | Project - name from GH Org|


# Performance

I've not put any effort into performance so far. I do not expect it to be particularly performant. 

There are a number of things that exist in the Milestone focused code that caches information so that it doesn't have to be fetched multiple times (eg project ID, tasks per project etc). I have not done the same here. There are some basic improvements that could be made (such as groups updates to task which are in the same repo). For now, I'm have only focused on the functionality.

I've also not looked at making any of the API calls asynchronous. This is something that could be done in the future.

One particularly bad symptom of the current implementation occurs due to the fact that the choice between "Single Repo" and "Assigned to me" is saved into the preferences. This means that when the app is restarted, it defaults to the users last choice. The down side of this it that it can result in a very slow initial load for the main window in "Assigned to me" mode as all of the issues must be fetch from the GitHub API, before the window is displayed. I believe that this should be fixed before merging this PR.


# Other Ideas - related to the "Assigned to me" mode

Some other ideas that are related to the "Assigned to me" mode. I've not implemented these yet, but they could be included in this PR, or in future PRs. In no particular order:

- Implement the "Multiple Projects, Assigned to me Mode"
- Offer Todoist "Sections" as part of the hierarchy.
- Options for the user to select which orgs they want to include (not just one or all)
- Assume everything within their personal org is assigned to them
- Allow users to select "just assigned to me, mentions, review requests, or all" etc
- Include or exclude pull requests
- Add labels in Todoist to match the labels in GitHub
- Add labels in Todoist to indicate which Tasks refer to GH issues and which refer to PRs
- Include "sort by" and/or "group by" options in then issue list in the UI
- Better ways to match existing tasks in Todoist to GitHub issues (eg add labels). Ideally this should tolerate the user moving tasks around, re-prioritising etc in Todoist, while still being able to match them to the correct GitHub issue.

# Other Ideas - unrelated to the "Assigned to me" mode

Other ideas that are unrelated to the "Assigned to me" mode that have occurred to be from using the tool. In no particular order:

- Command line options
- Sync-All mode (eg so that there is minimal interaction required)
- Visual indication when the sync is complete
- Install via `brew`
- Package for other platforms (eg Windows, Linux)
