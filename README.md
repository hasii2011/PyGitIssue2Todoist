<img width="34" height="17" src="./gittodoistclone/resources/gplv3-with-text-136x68.png"/> 
<a href="https://gitmoji.dev">
  <img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square" alt="Gitmoji">
</a>

[![Build Status](https://travis-ci.com/hasii2011/gittodoistclone.svg?branch=master)](https://travis-ci.com/hasii2011/gittodoistclone)

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

**Name:**   `.pyGitIssue2Todoist.ini`

**Location:**  `${HOME}`

```
[Github]
github_api_token = PutYourGithubKeyHere
github_user_name = PutYourGithubUserNameHere
github_url_option = Hyper Linked Task Name

[Todoist]
todoist_api_token = PutYourTodoistKeyHere
single_todoist_project = True
todoist_project_name = Development
clean_todoist_cache = True

[Main]
startup_width = 1024
startup_height = 768
startup_x = 0
startup_y = 0
```
PyGitIssue2Todoist provides access to the above options via a
configuration dialog.

# License

See [LICENSE](LICENSE)
