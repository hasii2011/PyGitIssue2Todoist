![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/agpl-license-web-badge-version-2-256x48.png "AGPL")

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
<a href="https://gitmoji.dev">
  <img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square" alt="Gitmoji">
</a>
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/hasii2011/PyGitIssue2Todoist/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/hasii2011/PyGitIssue2Todoist/tree/master)

# Introduction

This OS X application can read your GitHub repositories and convert your GitHub issues to todoist tasks.

# Translation

The translation is as follows:

* GitHub's repositories --> todoist projects
* GitHub's milestones   --> todoist top level tasks
* GitHub's issues       --> todoist subtasks under a top level task

If you don't use milestones and associate tasks with them the top-level task is called _All_.  There 
is an option to create creates repository sub-tasks inside a single top level project.  This allows 
users who are using the "community" version of Todoist to create sub-tasks for all their repositories inside 
a single task.  'Community' users are limited to 5 Todoist projects


# Requirements

The application gathers the following:

* A GitHub API token
* Your GitHub username
* A Todoist API token

The instructions on how to acquire/generate these tokens are [here](https://github.com/hasii2011/gittodoistclone/wiki).


# Format of the configuration file

**Name:**   `pyGitIssue2Todoist.ini`

**Location:**  `$HOME/.config/pygitissue2todoist/`

```
[GitHub]
gitHubAPIToken = PutYourGithubKeyHere
gitHubUserName = PutYourGithubUserNameHere
gitHubURLOption = Hyper Linked Task Name

[Todoist]
todoistAPIToken = PutYourTodoistKeyHere
singleTodoistProject = True
todoistProjectName = Development
cleanTodoistCache = True

[Main]
startupPosition = 32,32
startupSize = 1024,768

```
PyGitIssue2Todoist provides access to the above options via a
configuration dialog.

# License

See [LICENSE](LICENSE)

![Humberto's Modified Logo](https://raw.githubusercontent.com/wiki/hasii2011/gittodoistclone/images/SillyGitHub.png)

I am concerned about GitHub's Copilot project



I urge you to read about the
[Give up GitHub](https://GiveUpGitHub.org) campaign from
[the Software Freedom Conservancy](https://sfconservancy.org).

While I do not advocate for all the issues listed there, I do not like that
a company like Microsoft may profit from open source projects.

I continue to use GitHub because it offers the services I need for free.  But I continue
to monitor their terms of service.

Any use of this project's code by GitHub Copilot, past or present, is done
without my permission.  I do not consent to GitHub's use of this project's
code in Copilot.
