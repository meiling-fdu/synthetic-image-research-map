"""Shared country/region normalization for public map records."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional


CHINA_REGION_BY_CODE = {
    "HK": "Hong Kong",
    "MO": "Macau",
    "TW": "Taiwan",
}
CHINA_REGION_NAME_ALIASES = {
    "hong kong": "HK",
    "hong kong sar": "HK",
    "hong kong sar china": "HK",
    "hk": "HK",
    "macao": "MO",
    "macao sar": "MO",
    "macao sar china": "MO",
    "macau": "MO",
    "macau sar": "MO",
    "macau sar china": "MO",
    "mo": "MO",
    "taiwan": "TW",
    "taiwan province of china": "TW",
    "tw": "TW",
}


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def normalized_location_name(value: Any) -> str:
    return " ".join(
        re.sub(r"[^a-z0-9]+", " ", clean_text(value).casefold()).split()
    )


def normalize_country_region(
    country: Any,
    country_code: Any,
    region: Any = "",
    region_code: Any = "",
    raw_country: Optional[Any] = None,
    raw_country_code: Optional[Any] = None,
) -> Dict[str, str]:
    """Return canonical public location fields while retaining source values."""
    country_text = clean_text(country)
    country_code_source = clean_text(country_code)
    country_code_text = country_code_source.upper()
    region_text = clean_text(region)
    region_code_text = clean_text(region_code).upper()
    raw_country_text = (
        country_text if raw_country is None else clean_text(raw_country)
    )
    raw_country_code_text = (
        country_code_source
        if raw_country_code is None
        else clean_text(raw_country_code)
    )

    normalized_region_code = ""
    for code in (
        region_code_text,
        country_code_text,
        clean_text(raw_country_code_text).upper(),
    ):
        if code in CHINA_REGION_BY_CODE:
            normalized_region_code = code
            break

    if not normalized_region_code:
        for name in (region_text, country_text, raw_country_text):
            normalized_region_code = CHINA_REGION_NAME_ALIASES.get(
                normalized_location_name(name),
                "",
            )
            if normalized_region_code:
                break

    if normalized_region_code:
        return {
            "country": "China",
            "country_code": "CN",
            "region": CHINA_REGION_BY_CODE[normalized_region_code],
            "region_code": normalized_region_code,
            "raw_country": raw_country_text,
            "raw_country_code": raw_country_code_text,
        }

    return {
        "country": country_text or country_code_text,
        "country_code": country_code_text,
        "region": region_text,
        "region_code": region_code_text,
        "raw_country": raw_country_text,
        "raw_country_code": raw_country_code_text,
    }
