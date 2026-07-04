"""Conservative normalization and matching for human names."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Any, Mapping, Sequence


def _display_name(value: Any) -> str:
    if isinstance(value, Mapping):
        value = value.get("name") or value.get("author")
    return " ".join(str(value if value is not None else "").split())


def canonical_name_key(value: Any) -> str:
    """Return a case-folded, ASCII-folded, punctuation-free name key."""
    name = _display_name(value)
    if name.count(",") == 1:
        family, given = (part.strip() for part in name.split(",", 1))
        name = f"{given} {family}"
    text = unicodedata.normalize("NFKD", name).casefold()
    text = "".join(character for character in text if not unicodedata.combining(character))
    return " ".join(re.findall(r"[^\W_]+", text, flags=re.UNICODE))


def _ordered_tokens(value: Any) -> tuple[str, ...]:
    name = _display_name(value)
    if name.count(",") == 1:
        family, given = (part.strip() for part in name.split(",", 1))
        name = f"{given} {family}"
    return tuple(canonical_name_key(name).split())


def name_variants(value: Any) -> frozenset[str]:
    """Return only strong whole-name variants, never substring variants."""
    tokens = _ordered_tokens(value)
    if not tokens:
        return frozenset()
    variants = {" ".join(tokens)}
    if len(tokens) == 2:
        variants.add(" ".join(reversed(tokens)))
        variants.add("tokens:" + "|".join(sorted(tokens)))
    elif len(tokens) >= 3:
        variants.add(" ".join(reversed(tokens)))
        variants.add("tokens:" + "|".join(sorted(tokens)))
    return frozenset(variants)


def _token_matches(left: str, right: str) -> bool:
    return left == right or (
        min(len(left), len(right)) == 1
        and left[0] == right[0]
    )


def _ordered_tokens_match(
    left: Sequence[str], right: Sequence[str]
) -> bool:
    return len(left) == len(right) and all(
        _token_matches(left_token, right_token)
        for left_token, right_token in zip(left, right)
    )


def names_match(left: Any, right: Any) -> bool:
    """Match complete names while allowing safe order and initial variants."""
    left_tokens = _ordered_tokens(left)
    right_tokens = _ordered_tokens(right)
    if not left_tokens or not right_tokens:
        return False
    if left_tokens == right_tokens:
        return True

    if len(left_tokens) == 2 and len(right_tokens) == 2:
        return Counter(left_tokens) == Counter(right_tokens)

    if len(left_tokens) != len(right_tokens):
        return False
    if Counter(left_tokens) == Counter(right_tokens):
        return True
    if len(left_tokens) >= 3:
        return _ordered_tokens_match(left_tokens, right_tokens) or (
            _ordered_tokens_match(left_tokens, tuple(reversed(right_tokens)))
        )
    return False


def unique_matching_name(value: Any, candidates: Sequence[str]) -> str | None:
    """Return one matching candidate, rejecting ambiguous fuzzy matches."""
    exact_key = canonical_name_key(value)
    exact_matches = [
        candidate
        for candidate in candidates
        if canonical_name_key(candidate) == exact_key
    ]
    if len(exact_matches) == 1:
        return exact_matches[0]
    matches = [candidate for candidate in candidates if names_match(value, candidate)]
    return matches[0] if len(matches) == 1 else None
