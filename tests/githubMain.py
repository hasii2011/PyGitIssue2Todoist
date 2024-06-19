
from github import Github
from github.AuthenticatedUser import AuthenticatedUser
from github.Milestone import Milestone
from github.NamedUser import NamedUser

from pygitissue2todoist.general.PreferencesV2 import PreferencesV2

INTEGRATION_TOKEN: str = PreferencesV2().gitHubAPIToken
USERNAME:          str = 'hasii2011'

# Used for prototyping


def getIssuesInRepos():

    g = Github(INTEGRATION_TOKEN)

    user:  NamedUser | AuthenticatedUser = g.get_user(USERNAME)
    print(f'{user=}')

    repo = g.get_repo('hasii2011/PyUt')
    print(f'{repo=}')

    open_issues = repo.get_issues(state='open')
    print(f'**** list of milestone -- Release 7.0 issues')
    for issue in open_issues:       # type: ignore
        mileStone: Milestone = issue.milestone  # type: ignore
        if mileStone is not None and mileStone.title == 'Release 7.0':
            print(f'{issue=}')


def getMileStones():

    g = Github(INTEGRATION_TOKEN)
    repo = g.get_repo('hasii2011/PyUt')

    mileStones = repo.get_milestones(state='Open')
    for mileStone in mileStones:
        print(f'{mileStone}')


def getRepos():

    g = Github(INTEGRATION_TOKEN)

    user:  NamedUser | AuthenticatedUser = g.get_user(USERNAME)
    print(f'{user=}')

    repos = g.search_repositories(query='user:hasii2011')
    for repo in repos:
        print(f'{repo=}')


if __name__ == '__main__':
    # addSimpleTask()
    # getIssuesInRepos()
    # getRepos()
    getMileStones()
