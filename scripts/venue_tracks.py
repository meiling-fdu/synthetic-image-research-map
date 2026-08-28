"""Canonical paper-level track vocabulary, independent of venue/source titles."""
from __future__ import annotations
import re

VENUE_TRACKS = ("Main", "Workshop", "Tutorial", "Demo", "Challenge", "Short Paper",
                "Findings", "Poster", "Industry", "Doctoral Consortium", "Other")
ALLOWED_VENUE_TRACKS = set(VENUE_TRACKS)
_ALIASES = {value.casefold(): value for value in VENUE_TRACKS}
_ALIASES.update({"workshops": "Workshop", "tutorials": "Tutorial", "demos": "Demo",
                 "demonstration": "Demo", "demonstrations": "Demo", "challenges": "Challenge",
                 "short papers": "Short Paper", "posters": "Poster", "main track": "Main",
                 "workshop track": "Workshop", "industry track": "Industry", "demo track": "Demo"})


def normalize_venue_track(value):
    """Accept historical enum spellings, never alter bibliographic source text.

    Unknown values survive so validators/review queues can flag them; they are
    not coerced into Main or Other.
    """
    text = str(value or "").strip()
    key = re.sub(r"[_\s-]+", " ", text.casefold())
    return _ALIASES.get(key, text)
