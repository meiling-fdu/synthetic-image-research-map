#!/usr/bin/env python3
"""Canonical, conservative title casing for paper metadata."""

from __future__ import annotations

import re
from typing import Any, Dict, List


# These are lowercase only when they are not the first or last word of a title
# or subtitle. "based" is intentionally not included: English title case and
# the project's canonical example both use "Based on".
TITLE_CASE_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "as",
        "at",
        "but",
        "by",
        "for",
        "from",
        "in",
        "nor",
        "of",
        "on",
        "or",
        "per",
        "the",
        "to",
        "via",
        "vs",
        "with",
        "yet",
    }
)

# Case-insensitive corrections are deliberately limited to unambiguous,
# domain-wide acronyms. Existing mixed-case/all-capital author styling is
# preserved without needing an exhaustive registry of models and datasets.
CANONICAL_TECHNICAL_TOKENS = {
    token.casefold(): token
    for token in (
        "AI",
        "AIGC",
        "AIGI",
        "CLIP",
        "CNN",
        "DNN",
        "GAN",
        "GANs",
        "JPEG",
        "LLM",
        "OSN",
        "OSNs",
        "RGB",
        "SOTA",
        "VLM",
    )
}

WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
SUBTITLE_BOUNDARY_RE = re.compile(r"[:?!]|(?<=\s)[–—](?=\s)")
PROTECTED_METADATA_RE = re.compile(r"<[^>]*>|&[^;\s]+;|\\[A-Za-z]+")
HYPHEN_RE = re.compile(r"^[\-‐‑‒–—]")


def _has_intentional_case(word: str) -> bool:
    """Return whether a token already carries non-ordinary author styling."""
    letters = [character for character in word if character.isalpha()]
    if not letters:
        return True
    if len(letters) > 1 and all(character.isupper() for character in letters):
        return True
    first_cased = next(
        (index for index, character in enumerate(word) if character.isalpha()),
        None,
    )
    return bool(
        first_cased is not None
        and any(character.isupper() for character in word[first_cased + 1 :])
    )


def _capitalize_first_letter(word: str) -> str:
    for index, character in enumerate(word):
        if character.isalpha():
            return word[:index] + character.upper() + word[index + 1 :]
    return word


def canonical_paper_title(value: Any) -> str:
    """Apply canonical title case without changing punctuation or whitespace.

    Existing acronym/model/dataset styling is retained. Hyphenated components
    are treated as title words, so ``AI-generated`` and ``classical-quantum``
    become ``AI-Generated`` and ``Classical-Quantum`` respectively.
    """
    title = "" if value is None else str(value)
    protected_spans = [match.span() for match in PROTECTED_METADATA_RE.finditer(title)]
    matches = [
        match
        for match in WORD_RE.finditer(title)
        if not any(start <= match.start() < end for start, end in protected_spans)
    ]
    if not matches:
        return title
    letters = [
        match.group(0)
        for match in matches
        if any(character.isalpha() for character in match.group(0))
    ]
    if letters and all(word.upper() == word for word in letters):
        return title

    segment_ids: List[int] = [0]
    segment = 0
    for previous, current in zip(matches, matches[1:]):
        if SUBTITLE_BOUNDARY_RE.search(title[previous.end() : current.start()]):
            segment += 1
        segment_ids.append(segment)

    segment_first: Dict[int, int] = {}
    segment_last: Dict[int, int] = {}
    for index, segment_id in enumerate(segment_ids):
        segment_first.setdefault(segment_id, index)
        segment_last[segment_id] = index

    pieces: List[str] = []
    cursor = 0
    for index, match in enumerate(matches):
        pieces.append(title[cursor : match.start()])
        word = match.group(0)
        folded = word.casefold()
        segment_id = segment_ids[index]
        edge_word = index in {
            segment_first[segment_id],
            segment_last[segment_id],
        }
        if index + 1 < len(matches):
            following = title[match.end() : matches[index + 1].start()]
            preceding = (
                title[matches[index - 1].end() : match.start()]
                if index
                else ""
            )
            edge_word = edge_word or bool(
                HYPHEN_RE.match(following) and not HYPHEN_RE.match(preceding)
            )
        if folded in CANONICAL_TECHNICAL_TOKENS:
            replacement = CANONICAL_TECHNICAL_TOKENS[folded]
        elif folded in TITLE_CASE_STOP_WORDS and not edge_word:
            replacement = word.lower()
        elif _has_intentional_case(word):
            replacement = word
        else:
            replacement = _capitalize_first_letter(word.lower())
        pieces.append(replacement)
        cursor = match.end()
    pieces.append(title[cursor:])
    return "".join(pieces)
