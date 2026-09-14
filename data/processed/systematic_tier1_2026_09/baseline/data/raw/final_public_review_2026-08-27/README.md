# Focused public location evidence, 2026-08-27

Read-only Nominatim searches returned no named feature for these queries:

- `nawcwd-geocode.json`: Naval Air Warfare Center Weapons Division China Lake
- `dte-geocode.json`: Directorate of Technical Education Kanpur
- `irisking-geocode.json`: Beijing IrisKing

Endpoint: https://nominatim.openstreetmap.org/search; parameters `format=jsonv2`,
`addressdetails=1`, `extratags=1`, `namedetails=1`, plus the query above.

`nawcwd-named-buildings.json` is the unmodified response from
https://overpass-api.de/api/interpreter to:

```text
[out:json][timeout:25];nwr["name"~"Administration",i](35.65,-117.72,35.72,-117.62);out center tags;
```

No result was used as a coordinate. Empty responses do not prove that a facility
is absent. These queries do not cover the dormant institution backlog. PDFs and
rendered author pages were kept outside the repository in `/tmp/sirm-final-pass/`.
