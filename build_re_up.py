#!/usr/bin/env python3
"""The Re-Up's pages around the issues: home (the newest issue) and back issues; keeps the portraits in step."""
import datetime as dt, glob, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
DW = os.path.expanduser("~/.hermes/garden/doublewide")
sys.path.insert(0, ROOT)
import flipbook as fb   # noqa: E402
from flipbook import e   # noqa: E402

fb.CSS_FILE = "re-up.css"


def load(p):
    try:
        return json.load(open(p))
    except Exception:
        return {}


def issues():
    d = os.path.join(SITE, "issues")
    return sorted((f[:-5] for f in os.listdir(d) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.html", f)), reverse=True) if os.path.isdir(d) else []


def shell(title, body):
    css = open(os.path.join(ROOT, fb.CSS_FILE)).read()
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#1f7a6d">'
            '<link rel="icon" href="/icons/icon-192.png"><link href="https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Oswald:wght@400;600;700'
            '&family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet"><style>%s</style><script src="/app.js" defer></script>'
            '</head><body class="stand pub-ru">%s</body></html>' % (e(title), css, body))


def main():
    os.makedirs(os.path.join(SITE, "img"), exist_ok=True)
    for f in glob.glob(os.path.join(DW, "site", "img", "*.png")):
        dest = os.path.join(SITE, "img", os.path.basename(f))
        if not os.path.exists(dest) or os.path.getmtime(dest) < os.path.getmtime(f):
            shutil.copy2(f, dest)
    eds = issues()
    items = "".join('<li><a href="issues/%s.html">%s</a></li>' % (x, dt.date.fromisoformat(x).strftime("%A, %B %-d, %Y")) for x in eds)
    top = ('<header class="stand-top"><a class="stand-home ns-home" href="/" aria-label="The Corner Chronicle" title="The Corner Chronicle">🏠</a><a class="stand-home" href="./" aria-label="Today\'s ads">📌</a><div><h1>The Re-Up</h1>'
           '<div class="stand-sub">%s</div></div><a class="stand-home" href="archive.html" aria-label="Back issues">🗂</a></header>')
    open(os.path.join(SITE, "archive.html"), "w").write(shell("The Re-Up — Back Issues", (top % "every want-ad page") +
        '<main class="paper"><div class="box arch"><h2>The Re-Up</h2><ul class="archive">%s</ul></div></main>' % (items or "<li>None yet.</li>")))
    if eds:
        pg = open(os.path.join(SITE, "issues", eds[0] + ".html")).read()
        open(os.path.join(SITE, "index.html"), "w").write(pg.replace('href="../', 'href="').replace('src="../', 'src="'))
        ads = load(os.path.join(ROOT, "drafts", eds[0] + ".json")).get("want_ads") or []
        json.dump({"paper": "The Re-Up", "date": eds[0], "title": "%d want ads — %s" % (len(ads), ads[0].get("title") if ads else "nothing wanted"),
                   "url": "issues/%s.html" % eds[0], "issues": eds[:10]}, open(os.path.join(SITE, "latest.json"), "w"), ensure_ascii=False)
    else:
        open(os.path.join(SITE, "index.html"), "w").write(shell("The Re-Up", (top % "what the Garden needs") +
            '<main class="paper"><div class="box"><h2>The first Re-Up is on its way</h2><p>Every morning Ganja sets the want ads from the agents\' '
            'nightly reports: parts, permissions, logins and fixes they need from you — tap one to answer it.</p></div></main>'))
    print("re-up pages built")


if __name__ == "__main__":
    main()
