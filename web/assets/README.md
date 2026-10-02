# Homepage branding artwork

`synthetic-image-detection-attribution-landscape-logo.png` is the preserved original
2612 × 829 logo, including its obsolete title. The repository and its asset history
contain no separate text-free source.

`synthetic-image-forensics-mark.png` reuses only the globe, magnifier, location pin,
and chart illustration from that logo. It is a 728 × 692 pixel crop starting at
x = 4, y = 48 (top-left origin). No artwork was generated or redrawn, and no old
title text is included. The original file is unchanged.

Reproduce from the repository root on macOS:

```sh
sips --cropToHeightWidth 692 728 --cropOffset 48 4 \
  web/assets/synthetic-image-detection-attribution-landscape-logo.png \
  --out web/assets/synthetic-image-forensics-mark.png
```

The homepage treats the mark as decorative (`alt=""`). The canonical project title
and scope remain real HTML text. The hero's scoped `mix-blend-mode: multiply`
blends the artwork's existing light background into the site's header surface.
