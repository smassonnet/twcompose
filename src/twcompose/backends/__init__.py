from .abstract import AbstractCollectionBackend
from .docker import DockerCollectionBackend


def get_collections_backend() -> AbstractCollectionBackend:
    return DockerCollectionBackend()
