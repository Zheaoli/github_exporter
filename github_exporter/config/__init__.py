from typing import List

from github import Github
from prometheus_client import CollectorRegistry
from pydantic import BaseSettings

METRIC_REGISTRY = CollectorRegistry()


class Setting(BaseSettings):
    repo_names: List[str] = []
    github_token: str = ""


SETTING = Setting()

GITHUB_CLIENT = Github(SETTING.github_token)
