import abc
import dataclasses
import pathlib
from typing import Dict, Generic, TypeVar

from twcompose.compose import TwitterComposeModel

_T = TypeVar("_T")


@dataclasses.dataclass
class CollectorValueDifference(Generic[_T]):
    current: _T
    new: _T


class CollectorDoesNotExist(Exception):
    pass


class AbstractCollectionBackend(abc.ABC):
    """Abstract class for a backend to collect Tweet streams"""

    @abc.abstractmethod
    def diff(
        self,
        project_name: str,
        compose_config: TwitterComposeModel,
        credentials_file: pathlib.Path,
    ) -> Dict[str, CollectorValueDifference[str]]:
        """Differences between configuration and running stream collector

        Raises:
            CollectorDoesNotExist: If the collector is not already created,
                we cannot compute a diff
        """

    @abc.abstractmethod
    def update(
        self,
        project_name: str,
        compose_config: TwitterComposeModel,
        credentials_file: pathlib.Path,
    ) -> None:
        """Makes sure that the collection for a Twitter Token is running is the backend

        Args:
            project_name (str): The name of the tweet collection project
            compose_config (TwitterComposeModel): The configuration of twitter compose
            twitter_token (str): The twitter token
        """

    @abc.abstractmethod
    def stop(self, project_name: str) -> None:
        """Makes sure the collection associated to the given project name is stopped

        Args:
            project_name (str): The name of the tweet collection project
        """

    @abc.abstractmethod
    def is_running(self, project_name: str) -> bool:
        """Tells whether the Twitter stream collection is running for a given project

        Args:
            project_name (str): The name of the tweet collection project

        Returns:
            bool: True if the collection is running the project
        """
