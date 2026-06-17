import json
import logging 
from dataclasses import dataclass
from app.services.parser import FileDiff, LineType

logger = logging.getLogger(__name__)

@dataclass
class Comment:
    path: str
    line: int
    body: str

def parser_llm_response(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse LLM response as JSON: %s", e)
        logger.debug("LLM response content: %s", text)
        return []
    
    if not isinstance(data, list):
        logger.error("LLM response JSON is not a list: %s", data)
        return []
    
    return data


def validate_comment(raw_c: list[dict], file_diffs: list[FileDiff]) -> list[Comment]:
    comments: dict[str,set[int]] = {}
    for fd in file_diffs:
        valid_lines: set[int] = set()
        for hunk in fd.hunks:
            for line in hunk.lines:
                if line.type in (LineType.ADDED, LineType.CONTEXT):
                    if line.new_lineno is not None:
                        valid_lines.add(line.new_lineno)
        comments[fd.path] = valid_lines

    valid_comments: list[Comment] = []
    for item in raw_c:
        if not all(k in item for k in ("path", "line", "comment")):
            logger.warning("Skipping invalid comment item (missing keys): %s", item)
            continue

        path = item["path"]
        line = item["line"]

        if path not in comments:
            logger.warning("Skipping comment for unknown file path: %s", path)
            continue

        if line not in comments[path]:
            logger.warning("Skipping comment for invalid line number %s in file %s", line, path)
            continue

        valid_comments.append(Comment(path=path, line=line, body=item["comment"]))

    return valid_comments