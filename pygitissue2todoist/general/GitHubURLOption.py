
from enum import Enum


class GitHubURLOption(Enum):

    DoNotAdd            = 'Do not add'
    AddAsDescription    = 'Add as description'
    AddAsComment        = 'Add as comment'
    HyperLinkedTaskName = 'Hyper Linked Task Name'

    def __str__(self):
        return str(self.name)
