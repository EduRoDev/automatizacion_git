import logging
from app.models.github import PullRequestEvent
from app.services.client import fetch_diff
from app.services.parser import parser

logger = logging.getLogger(__name__)

async def process_pull_request(event: PullRequestEvent) -> None:
    pr = event.pull_request
    logger.info("Processing PR #%s in %s", pr.number, event.repository.full_name)

    diff_text = await fetch_diff(pr.diff_url)
    file_diffs = parser(diff_text)
    for fd in file_diffs:
       logger.info("%s -> (new: %s, deleted: %s)", fd.path, len(fd.added_lines), len(fd.removed_lines))
