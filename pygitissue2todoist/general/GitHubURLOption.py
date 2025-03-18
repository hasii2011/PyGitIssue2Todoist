
from enum import Enum


class GitHubURLOption(Enum):

    DoNotAdd            = 'Do not add'
    AddAsDescription    = 'Add as description'
    AddAsComment        = 'Add as comment'
    HyperLinkedTaskName = 'Hyper Linked Task Name'

    def __str__(self):
        return str(self.name)

    @classmethod
    def deSerialize(cls, value: str) -> 'GitHubURLOption':

        match value:
            case GitHubURLOption.DoNotAdd.value:
                gitHubUrlOption: GitHubURLOption = GitHubURLOption.DoNotAdd
            case GitHubURLOption.AddAsDescription.value:
                gitHubUrlOption = GitHubURLOption.AddAsDescription
            case GitHubURLOption.AddAsComment.value:
                gitHubUrlOption = GitHubURLOption.AddAsComment
            case GitHubURLOption.HyperLinkedTaskName.value:
                gitHubUrlOption = GitHubURLOption.HyperLinkedTaskName
            case _:
                raise Exception('Unknown GitHubURLOption')

        return gitHubUrlOption
