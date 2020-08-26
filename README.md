# Introduction

This mac application can read your github repositories and converts your github issues to todoist tasks.

# Translation

The translation is as follows:

Github repositories --> todoist projects
Github milestones   --> todoist top level tasks
Github issues       --> todoist subtasks under a top level task

If you don't use milestones and associate tasks with them the top-level task is called "All"

# Requirements

The application gathers the following:

* A Github API token
* Your Github username
* A Todoist API token

# How to generate tokens

## Github

## Todoist



# Format of configuration file





`[Github]`
`github_api_token = PutYourGithubKeyHere`
`github_user_name = PutYourGithubUserNameHere`

`[Todoist]`
`todoist_api_token = PutYourTodoistKeyHere`

`[Main]`
`startup_width = 1024`
`startup_height = 768`
`startup_x = -1`
`startup_y = -1`

