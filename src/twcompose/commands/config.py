import yaml
from twcollect.config import CredentialsModel

from twcompose.compose import TwitterComposeModel


def config_command(
    project_name: str,
    compose_config: TwitterComposeModel,
    credentials: CredentialsModel,
):
    """Prints configuration after parsing"""
    print(yaml.safe_dump(compose_config.dict()))
