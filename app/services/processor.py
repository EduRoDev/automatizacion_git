import logging
from app.models.github import PullRequestEvent
from app.services.client import fetch_diff, comment
from app.services.parser import parser
from app.services.llm import review_diff


logger = logging.getLogger(__name__)

async def process_pull_request(event: PullRequestEvent) -> None:
    pr = event.pull_request
    logger.info("Processing PR #%s in %s", pr.number, event.repository.full_name)

    diff_text = await fetch_diff(pr.diff_url)
    file_diffs = parser(diff_text)
    for fd in file_diffs:
        logger.info("%s -> (new: %s, deleted: %s)", fd.path, len(fd.added_lines), len(fd.removed_lines))
        try:
            review = await review_diff(diff_text)
            logger.info("Review generated for PR #%s, posting comment", pr.number)

            await comment(event.repository.full_name, pr.number, review)
            logger.info("Commented on PR #%s", pr.number)
        except Exception:
            logger.exception("Error on PR #%s", pr.number)