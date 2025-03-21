
from typing import Callable

from abc import ABC
from abc import abstractmethod

from pygitissue2todoist.strategy.StrategyTypes import CloneInformation


class ITodoistCreationStrategy(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def createTasks(self, info: CloneInformation, progressCb: Callable):
        """
        Abstract method;  Subclass must implement
        Args:
            info:           The Clone information from the GitHub calls
            progressCb:     The callback to report information
        """
        pass

    @abstractmethod
    def _determineProjectIdFromRepoName(self, info: CloneInformation, progressCb: Callable) -> str:
        """
        Either gets a project ID from the repo name or one for the user specified project

        Args:
            info:  The cloned information
            progressCb: A progress callback to return status

        Returns:  An appropriate parent ID for newly created tasks
        """
        pass
