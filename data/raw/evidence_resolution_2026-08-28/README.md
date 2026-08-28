# Scoped site evidence cache — 2026-08-28

Unmodified OpenStreetMap/Nominatim responses; OSM contributors, ODbL 1.0. Only two active location cases queried. No dormant-institution geocoding.

- `kumoh-search.json`: https://nominatim.openstreetmap.org/search?q=Kumoh%20National%20Institute%20of%20Technology&format=jsonv2&addressdetails=1&namedetails=1
  SHA-256: `ed5670b6e7f1c8e0547ba0cd037877f606666a541f9c7118d047820e2a74b4af`
- `kumoh-campus.osm`: https://www.openstreetmap.org/api/0.6/map?bbox=128.386,36.141,128.397,36.150
  SHA-256: `8cea3a247bf008c126bb83b5c4302b1413e13feae7010f0d1010609df48057d8`
- `nawc-address-search.json`: https://nominatim.openstreetmap.org/search?q=1%20Administration%20Circle%20China%20Lake&format=jsonv2&addressdetails=1
  SHA-256: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`

Kumoh: named university building way 1518535866, 산학협력관. Representative point (36.148713, 128.3932287) is the midpoint of the longest interior horizontal segment at the footprint bounding-box middle latitude (even–odd edge intersections), rounded to seven decimals. Campus way 234847049 confirms 61 Daehak-ro. This is a building-derived point, not a geocoder city centroid. Official 2018/2020 center brochures identify Room 408; no floor-specific coordinates are claimed.

NAWCWD exact-address search returned an empty array; no coordinates accepted.
