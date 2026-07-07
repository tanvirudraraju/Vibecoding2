#!/usr/bin/env bash
# Vastra — double-click to (re)launch the scroll-cinematic demo.
cd "$(dirname "$0")"
PORT=5005
echo "vastra demo → http://127.0.0.1:$PORT/"
(command -v open >/dev/null && sleep 1 && open "http://127.0.0.1:$PORT/") &
python3 -m http.server "$PORT"
