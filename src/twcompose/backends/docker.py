import dataclasses
import pathlib
from typing import Dict, List, Optional, Set, Tuple

import docker
import docker.errors
from docker.models.containers import Container

from twcompose.backends.abstract import (
    AbstractCollectionBackend,
    CollectorDoesNotExist,
    CollectorValueDifference,
)
from twcompose.compose import TwitterComposeModel


def get_command_from_container(container: Container) -> List[str]:
    """Returns the command of a docker container"""
    return container.attrs["Args"]


def get_volumes_map_from_container(container: Container) -> Set[str]:
    """Returns a list of container volumes as <src>:<dest>"""
    return {f"{m['Source']}:{m['Destination']}" for m in container.attrs["Mounts"]}


def get_image_name_from_container(container: Container) -> str:
    """Returns the full image name of the container"""
    return container.attrs["Config"]["Image"]


def _volume_set_to_str(volumes: Set[str]) -> str:
    return " ; ".join(sorted(volumes))


def _command_to_str(command: List[str]) -> str:
    return " ".join(command)


@dataclasses.dataclass
class DockerCollectionBackend(AbstractCollectionBackend):
    docker_client: docker.DockerClient = dataclasses.field(
        default_factory=docker.from_env
    )

    def get_container_name(self, project_name: str) -> str:
        return f"stream_{project_name}"

    def get_container(self, project_name: str) -> Optional[Container]:
        """Get the container for the Tweet collection project"""
        try:
            return self.docker_client.containers.get(
                self.get_container_name(project_name)
            )
        except docker.errors.NotFound:
            return None

    def _get_container_image(self, compose_config: TwitterComposeModel) -> str:
        return f"{compose_config.image_name}:{compose_config.image_tag}"

    def _get_container_command(self, compose_config: TwitterComposeModel) -> List[str]:
        command_parameters: List[str] = ["-c", "/app/credentials.yml"]

        stream_parameters = compose_config.parameters.to_querystring()
        if stream_parameters:
            command_parameters += ["-p", stream_parameters]

        if "max_file_size" in compose_config.output.options:
            command_parameters += [
                "--max-file-size",
                str(compose_config.output.options["max_file_size"]),
            ]
        return command_parameters + ["/app/output"]

    def _get_volumes(
        self, compose_config: TwitterComposeModel, credentials_file: pathlib.Path
    ) -> Set[str]:
        output_folder = pathlib.Path(compose_config.output.path).absolute()
        return {
            f"{credentials_file.absolute()}:/app/credentials.yml",
            f"{output_folder}:/app/output",
        }

    def diff(
        self,
        project_name: str,
        compose_config: TwitterComposeModel,
        credentials_file: pathlib.Path,
    ) -> Dict[str, CollectorValueDifference[str]]:
        container = self.get_container(project_name)

        if container is None:
            raise CollectorDoesNotExist()

        # Getting attribute name, actual_value, expected_value
        attributes: List[Tuple[str, str, str]] = [
            (
                "image_name",
                get_image_name_from_container(container),
                self._get_container_image(compose_config),
            ),
            (
                "volumes",
                _volume_set_to_str(get_volumes_map_from_container(container)),
                _volume_set_to_str(self._get_volumes(compose_config, credentials_file)),
            ),
            (
                "command",
                _command_to_str(get_command_from_container(container)),
                _command_to_str(self._get_container_command(compose_config)),
            ),
        ]

        return {
            name: CollectorValueDifference(current=actual, new=expected)
            for name, actual, expected in attributes
            if actual != expected
        }

    def _run_container(
        self,
        project_name: str,
        compose_config: TwitterComposeModel,
        credentials_file: pathlib.Path,
    ) -> None:
        """Runs the streams collector container"""
        self.docker_client.containers.run(
            image=self._get_container_image(compose_config),
            command=self._get_container_command(compose_config),
            name=self.get_container_name(project_name),
            volumes=list(self._get_volumes(compose_config, credentials_file)),
            restart_policy={"Name": "on-failure", "MaximumRetryCount": 10},
            detach=True,
        )

    def update(
        self,
        project_name: str,
        compose_config: TwitterComposeModel,
        credentials_file: pathlib.Path,
    ) -> None:
        """Runs the collection in a docker container"""
        try:
            needs_update = (
                len(self.diff(project_name, compose_config, credentials_file)) > 0
            )
        except CollectorDoesNotExist:
            needs_update = True
        existing_container = self.get_container(project_name)

        # If there is an existing container and no need to update,
        # we start it and return
        if existing_container and not needs_update:
            existing_container.start()
            return

        # If there is a container, we need to stop and remove it
        # before starting a new one
        if existing_container and needs_update:
            existing_container.stop()
            existing_container.remove()

        self._run_container(project_name, compose_config, credentials_file)

    def stop(self, project_name: str) -> None:
        container = self.get_container(project_name)
        if container is not None:
            container.stop()

    def is_running(self, project_name: str) -> bool:
        container = self.get_container(project_name)
        if container is None:
            return False

        return container.status == "running"
