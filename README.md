# vastra — scroll-cinematic site

A 3D-scroll (canvas image-sequence scrub) site for **Vastra**, an Indian ethnic
clothing brand. Two sticky-canvas cinematic sections are scrubbed by scroll,
with smooth-lerped progress, scroll-synced overlay copy, and reveal-on-scroll
content sections. Zero build — plain HTML/CSS/JS from any static server.

## Run it

```bash
python3 -m http.server 5005   # from the repo root
# → http://127.0.0.1:5005/
```

or double-click `Launch Demo.command`.

## Structure

- `index.html` — all sections + the `SCRUB_SECTIONS` config (bottom of file)
- `scroll-cinematic.js` — the scrub engine (preload, cover-fit HiDPI canvas, lerped progress, overlay fade windows)
- `styles.css` — brand system (cream / terracotta / gold, Fraunces + Inter)
- `frames/hero/`, `frames/zari/` — 160 numbered JPGs per scrub section
- `scripts/render-placeholder-frames.py` — generated the current placeholder sequences
- `scripts/extract-frames.sh`, `scripts/compress-frames.sh` — ffmpeg pipeline for real clips

## Swapping in the Higgsfield clips

The current frames are **procedural placeholders** — the Higgsfield workspace
had 0 credits at build time. Once credits are available:

1. Generate a 16:9 hero keyframe (`nano_banana_pro`), then two 6s 1080p clips
   (`seedance_2_0`, start_image = keyframe job id):
   - hero: slow cinematic push-in/orbit on the model in embroidered silk
   - zari: macro reveal of gold zari embroidery assembling / being woven
2. Download each clip, then:
   ```bash
   scripts/extract-frames.sh hero.mp4 frames/hero 160
   scripts/compress-frames.sh frames/hero 1600 88
   scripts/extract-frames.sh zari.mp4 frames/zari 160
   scripts/compress-frames.sh frames/zari 1600 88
   ```
3. If the clip count differs from 160, update `frameCount` in `SCRUB_SECTIONS`
   at the bottom of `index.html`. Nothing else changes.
