"""Publication rules shared by public export and validation."""

from __future__ import annotations

import re
from typing import Any, Mapping


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _boolean(value: Any) -> bool:
    return value is True or _text(value).casefold() in {"1", "true", "yes", "y"}


def paper_is_retracted(row: Mapping[str, Any]) -> bool:
    publication_type = _text(row.get("publication_type")).casefold()
    title = _text(row.get("title")).casefold()
    exclusion_reason = _text(row.get("exclusion_reason")).casefold()
    notes = _text(row.get("notes")).casefold()
    return (
        publication_type in {"retraction", "retracted"}
        or any(_boolean(row.get(field)) for field in ("is_retracted", "retracted"))
        or bool(re.match(r"^(?:\[\s*retracted\s*\]|retracted\s*:)", title))
        or "retracted" in exclusion_reason
        or "retraction" in exclusion_reason
        or "retracted" in notes
    )
