#!/usr/bin/env bash
# Resize + recompress a frame folder for fast preloading.
# Usage: compress-frames.sh <frames-dir> [max-width] [quality]
set -euo pipefail
FFMPEG="$(command -v ffmpeg || echo /tmp/ffmpeg-bin/ffmpeg)"
DIR="$1"; WIDTH="${2:-1600}"; Q="${3:-88}"
QV=$(python3 -c "print(max(2, round(31 - $Q * 29 / 100)))")
for f in "$DIR"/frame_*.jpg; do
  "$FFMPEG" -y -loglevel error -i "$f" -vf "scale='min($WIDTH,iw)':-2" -q:v "$QV" "$f.tmp.jpg"
  mv "$f.tmp.jpg" "$f"
done
echo "compressed $(ls "$DIR"/frame_*.jpg | wc -l) frames in $DIR (max ${WIDTH}px, q$Q)"
