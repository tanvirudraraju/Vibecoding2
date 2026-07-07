#!/usr/bin/env bash
# Slice a cinematic clip into numbered JPG scroll frames.
# Usage: extract-frames.sh <clip.mp4> <out-dir> [frame-count]
set -euo pipefail
FFMPEG="$(command -v ffmpeg || echo /tmp/ffmpeg-bin/ffmpeg)"
CLIP="$1"; OUT="$2"; COUNT="${3:-180}"
mkdir -p "$OUT"
DUR=$("$FFMPEG" -i "$CLIP" 2>&1 | grep -oP 'Duration: \K[0-9:.]+' | awk -F: '{print $1*3600+$2*60+$3}')
FPS=$(python3 -c "print(f'{$COUNT/$DUR:.4f}')")
"$FFMPEG" -y -i "$CLIP" -vf "fps=$FPS" -q:v 2 "$OUT/frame_%04d.jpg"
# renumber to 0-based to match the engine's framePath
i=0
for f in "$OUT"/frame_*.jpg; do
  mv "$f" "$OUT/tmp_$(printf '%04d' $i).jpg"; i=$((i+1))
done
for f in "$OUT"/tmp_*.jpg; do mv "$f" "${f/tmp_/frame_}"; done
echo "extracted $i frames -> $OUT"
