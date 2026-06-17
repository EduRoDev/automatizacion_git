from pydantic import BaseModel, ConfigDict


class _Lenient(BaseModel):
    model_config = ConfigDict(extra="ignore")

class Repository(_Lenient):
    full_name: str

class Head(_Lenient):
    sha: str

class PullRequest(_Lenient):
    number: int
    title: str
    state: str
    diff_url: str
    head: Head

class PullRequestEvent(_Lenient):
    action: str
    number: int
    pull_request: PullRequest
    repository: Repository

    @property
    def is_actionable(self)-> bool:
        return self.action in {"opened","reopened","synchronize"}