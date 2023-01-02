import pathlib

from twcompose.backends import get_collections_backend
from twcompose.compose import TwitterComposeModel
from twcompose.utils import ensure_backend_stopped


def stop_command(
    project_name: str,
    compose_config: TwitterComposeModel,
    credentials: pathlib.Path,
):
    backend = get_collections_backend()
    ensure_backend_stopped(backend, project_name)
