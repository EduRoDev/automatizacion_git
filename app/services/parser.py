from __future__ import annotations
import re
from dataclasses import dataclass, field
from enum import StrEnum


class LineType(StrEnum):
    ADDED = "added"
    REMOVED = "removed"
    CONTEXT = "context"


@dataclass
class DiffLine:
    type: LineType
    content: str
    new_lineno: int | None = None
    old_lineno: int | None = None


@dataclass
class DiffHunk:
    old_start: int
    new_start: int
    lines: list[DiffLine] = field(default_factory=list)


@dataclass
class FileDiff:
    old_path: str
    new_path: str
    hunks: list[DiffHunk] = field(default_factory=list)
    is_new: bool = False
    is_deleted: bool = False

    @property
    def path(self) -> str:
        return self.old_path if self.is_deleted else self.new_path

    @property
    def added_lines(self) -> list[DiffLine]:
        return [line for h in self.hunks for line in h.lines if line.type is LineType.ADDED]

    @property
    def removed_lines(self) -> list[DiffLine]:
        return [line for h in self.hunks for line in h.lines if line.type is LineType.REMOVED]


_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def parser(diff_text: str) -> list[FileDiff]:
    files: list[FileDiff] = []
    current_file: FileDiff | None = None
    current_hunk: DiffHunk | None = None
    old_lineno = new_lineno = 0

    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            current_file = FileDiff(old_path="", new_path="")
            files.append(current_file)
            current_hunk = None
            continue

        if current_file is None:
            continue

        if line.startswith("new file"):
            current_file.is_new = True
            continue
        if line.startswith("deleted file"):
            current_file.is_deleted = True
            continue

        if line.startswith("--- "):
            current_file.old_path = _strip_path_prefix(line[4:])
            continue
        if line.startswith("+++ "):
            current_file.new_path = _strip_path_prefix(line[4:])
            continue

        match = _HUNK_RE.match(line)
        if match:
            old_start, new_start = int(match.group(1)), int(match.group(2))
            current_hunk = DiffHunk(old_start=old_start, new_start=new_start)
            current_file.hunks.append(current_hunk)
            old_lineno, new_lineno = old_start, new_start
            continue

        if current_hunk is None:
            continue

        if line.startswith("+"):
            current_hunk.lines.append(
                DiffLine(LineType.ADDED, line[1:], new_lineno=new_lineno)
            )
            new_lineno += 1
        elif line.startswith("-"):
            current_hunk.lines.append(
                DiffLine(LineType.REMOVED, line[1:], old_lineno=old_lineno)
            )
            old_lineno += 1
        elif line.startswith(" "):
            current_hunk.lines.append(
                DiffLine(
                    LineType.CONTEXT, line[1:],
                    old_lineno=old_lineno, new_lineno=new_lineno,
                )
            )
            old_lineno += 1
            new_lineno += 1

    return files


def _strip_path_prefix(path: str) -> str:
    path = path.strip()
    if path.startswith(("a/", "b/")):
        return path[2:]
    return path
