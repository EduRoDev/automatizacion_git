import logging
from app.models.github import PullRequestEvent
from app.services.client import fetch_diff, comment_on_line
from app.services.parser import parser
from app.services.llm import review_diff
from app.services.review import parser_llm_response, validate_comment


logger = logging.getLogger(__name__)

async def process_pull_request(event: PullRequestEvent) -> None:
    pr = event.pull_request
    logger.info("Processing PR #%s in %s", pr.number, event.repository.full_name)

    diff_text = await fetch_diff(pr.diff_url)
    file_diffs = parser(diff_text)

    for fd in file_diffs:
        logger.info("%s -> (new: %s, deleted: %s)", fd.path, len(fd.added_lines), len(fd.removed_lines))

    try:
        raw = await review_diff(diff_text)
        observaciones = parser_llm_response(raw)
        comentarios = validate_comment(observaciones, file_diffs)

        logger.info(
            "PR #%s: %s observaciones del modelo, %s válidas",
            pr.number, len(observaciones), len(comentarios),
        )

        for c in comentarios:
            await comment_on_line(
                event.repository.full_name,
                pr.number,
                pr.head.sha,
                c.path,
                c.line,
                c.body,
            )

        logger.info("PR #%s: %s comentarios inline publicados", pr.number, len(comentarios))
    except Exception:
        logger.exception("Error al revisar o comentar el PR #%s", pr.number)