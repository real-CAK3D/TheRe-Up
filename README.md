# The Re-Up

The Garden's want-ads paper: what the agents need from you — parts, permissions, logins, fixes — plus the odd FREE / FOR SALE ad. Tap an ad to have the agent handle it, do it yourself, or pass; the result shows under the ad.

Part of the Garden's papers, all read through **[The Corner Chronicle](https://github.com/real-CAK3D/NewsStand)** — one home-screen app that mounts every paper under one private (Tailscale-only) HTTPS address: [The Double Wide](https://github.com/real-CAK3D/TheDoubleWide) (daily), [The Re-Up](https://github.com/real-CAK3D/TheRe-Up) (want ads), [The Sunday Smoke](https://github.com/real-CAK3D/TheSundaySmoke) (Sundays), [Roach Clips](https://github.com/real-CAK3D/RoachClips) (Tuesdays) and [The Green Thumb](https://github.com/real-CAK3D/TheGreenThumb) (the directory). The papers are written by [Hermes](https://github.com/NousResearch/hermes-agent) agents running on a small Oracle VM called The Garden.

## Files

| File | What it does |
|---|---|
| `render_re_up.py` | Prints the day's want ads as a flipbook of classifieds. |
| `build_re_up.py` | Home page and back issues. |
| `serve.py` | Answer an ad: approvals go to Ganja as a one-off Hermes job; follow-ups read her report. |
| `gardenweb.py` | The small shared web-server kit every Garden paper carries its own copy of. |

## Running

Ganja sets the ads each morning with The Double Wide; served at `/re-up/` under The Corner Chronicle. Each project is Linux-first (`%-d` date formatting) and expects a Hermes install on the same machine.
