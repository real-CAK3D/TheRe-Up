#!/usr/bin/env python3
"""The Re-Up web server (Tailscale-only; mounted at /re-up/ under the Newsstand).

  GET  /api/jobs?date=YYYY-MM-DD       -> each ad's state ("want:<idx>": approved + result / done / dismissed)
  POST /api/jobs {date, kind: "want", idx, decision: approve | done | dismiss}
        "approve" hands the ad (read from disk, never from the browser) to Ganja as a one-off Hermes job.
Usage: serve.py <site_dir> <host> <port>
"""
import datetime as dt, glob, os, re, subprocess, sys

import gardenweb as gw
from gardenweb import jload, jsave, LOCK

ROOT = os.path.dirname(os.path.abspath(__file__))
HERMES = os.path.expanduser("~/.hermes")
PY = os.path.join(HERMES, "hermes-agent/venv/bin/python")
RESULT_RULE = ("START your final reply with exactly one line: 'RESULT: OK — <what worked>', 'RESULT: FAILED — <what went wrong>' or "
               "'RESULT: NEEDS CAK3D — <the step he must do>'. The Re-Up shows that line under the ad, so keep it under 120 characters.")


def hand_to_ganja(date, idx, ad):
    prompt = (
        "CAK3D answered this want ad in THE RE-UP (%s, ad #%d) — 'Yes, have the agent handle it':\n- Ad: %s\n- Placed by: %s\n- Details: %s\n- Ask: %s\n\n"
        "Carry it out now if the Garden agents can do it (inspect first, back up before changes, keep a rollback path, never print or store secrets). "
        "If it genuinely needs CAK3D's own hands — buying something, clicking in a web console, physical access, an interactive login — don't pretend: "
        "give short, exact steps. Never buy anything or create accounts. Your final reply is posted to Discord. " + RESULT_RULE
    ) % (date, idx + 1, ad.get("title"), ad.get("agent") or "unknown", ad.get("text") or ad.get("details") or "", ad.get("ask") or "")
    code = ("import sys; from cron.jobs import create_job\n"
            "j = create_job(sys.argv[1], '1m', name=sys.argv[2], repeat=1, deliver='discord')\n"
            "print(j.get('id') if isinstance(j, dict) else j)")
    r = subprocess.run([PY, "-c", code, prompt, "Re-Up ad: " + str(ad.get("title"))[:60]], cwd=os.path.join(HERMES, "hermes-agent"),
                       env={**os.environ, "HERMES_HOME": HERMES}, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        return False, r.stderr.strip()[-200:]
    return True, (r.stdout.strip().splitlines() or [""])[-1]


def followup(date):
    f = os.path.join(ROOT, "jobs", date + ".json")
    st, changed = jload(f, {}), False
    for v in st.values():
        jid = v.get("hermes_job")
        if v.get("status") != "approved" or v.get("result_status") or not re.fullmatch(r"[0-9a-f]{6,32}", str(jid or "")):
            continue
        outs = sorted(glob.glob(os.path.join(HERMES, "cron", "output", jid, "*.md")))
        if not outs:
            continue
        txt = open(outs[-1], errors="ignore").read()
        m = re.search(r"RESULT:\s*(OK|FAILED|NEEDS CAK3D)\s*[—\-:]*\s*(.*)", txt[txt.rfind("## Response"):] if "## Response" in txt else txt)
        v["result_status"] = {"OK": "ok", "FAILED": "failed", "NEEDS CAK3D": "needs"}[m.group(1)] if m else "ok"
        v["result"] = (m.group(2).strip() if m else "finished — see Discord")[:160]
        changed = True
    if changed:
        with LOCK:
            jsave(f, st)
    return st


class Handler(gw.Handler):
    ROOT = ROOT

    def get_api(self, p):
        if p == "/api/jobs":
            m = re.search(r"date=(\d{4}-\d{2}-\d{2})", self.path)
            self.json(200, followup(m.group(1)) if m else {})
            return True

    def post_api(self, p):
        if p != "/api/jobs":
            return False
        req = self.body()
        try:
            date, idx, decision = str(req.get("date")), int(req.get("idx")), str(req.get("decision"))
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) and decision in ("approve", "done", "dismiss") and req.get("kind") == "want"
            ad = (jload(os.path.join(ROOT, "drafts", date + ".json"), {}).get("want_ads") or [])[idx]
        except Exception:
            self.json(400, {"ok": False, "message": "That ad couldn't be found."})
            return True
        key, f = "want:%d" % idx, os.path.join(ROOT, "jobs", date + ".json")
        with LOCK:
            st = jload(f, {})
            if decision == "approve" and st.get(key, {}).get("status") == "approved":
                self.json(200, {"ok": True, "message": "Already on it."})
                return True
            entry = {"status": {"approve": "approved", "done": "done", "dismiss": "dismissed"}[decision], "kind": "want",
                     "at": dt.datetime.now().isoformat(timespec="seconds"), "title": ad.get("title"), "agent": "Ganja"}
            if decision == "approve":
                ok, info = hand_to_ganja(date, idx, ad)
                if not ok:
                    self.json(500, {"ok": False, "message": "Couldn't hand it to Ganja: " + info})
                    return True
                entry["hermes_job"] = info
            st[key] = entry
            jsave(f, st)
        self.json(200, {"ok": True, "message": {"approve": "On it! Ganja takes it from here — the result shows under the ad and in Discord.",
                                                "done": "Marked done — thanks!", "dismiss": "Okay, passed on this one."}[decision]})
        return True


if __name__ == "__main__":
    gw.run(Handler, sys.argv[1], sys.argv[2], int(sys.argv[3]))
