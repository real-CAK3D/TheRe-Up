#!/usr/bin/env bash
# After Ganja sets today's want ads: print The Re-Up and ring the Newsstand's bell (only when there are ads).
set -u
D="$HOME/.hermes/garden/re-up"; PY="$HOME/.hermes/hermes-agent/venv/bin/python"; T=$(TZ=America/New_York date +%F)
F="$D/drafts/$T.json"; [ -f "$F" ] || { echo "no Re-Up draft for $T"; exit 0; }
cd "$D" && "$PY" "$D/render_re_up.py" "$F" || exit 1
N=$("$PY" -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["want_ads"]))' "$F" 2>/dev/null)
[ "${N:-0}" -gt 0 ] && "$PY" "$HOME/.hermes/garden/newsstand/notify.py" "📌 The Re-Up: ${N} want ads" "The agents need a few things from you." "/re-up/"
exit 0
