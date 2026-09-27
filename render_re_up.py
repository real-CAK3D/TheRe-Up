#!/usr/bin/env python3
"""Render THE RE-UP — the Garden's want-ads paper: what the agents need from CAK3D (parts, permissions, logins, fixes),
plus the odd FREE / FOR SALE ad. Ganja writes it each morning with The Double Wide; every ad is tappable.

Usage: render_re_up.py drafts/<date>.json -> site/issues/<date>.html, then build_re_up.py refreshes home + back issues.
Uses its own copy of The Double Wide's flipbook (flipbook.py) with its own masthead and stylesheet.
"""
import datetime as dt, json, os, sys

import flipbook as fb
from flipbook import e, page, SEAL, back_codes

fb.CSS_FILE = "re-up.css"
ROOT, SITE = fb.ROOT, fb.SITE
KEYS = ("title", "agent", "details", "text", "ask", "url")


def render(ed):
    date = ed["date"]
    d = dt.date.fromisoformat(date)
    no = (d - dt.date(2026, 9, 27)).days + 1
    ads = [a for a in ed.get("want_ads") or [] if isinstance(a, dict)]
    front = page("The Re-Up", (
        '<div class="gum"><span>WANTED · FREE · FOR SALE · THE GARDEN</span></div>'
        '<div class="pc-top"><a class="seal" href="/" aria-label="Back to the Newsstand" title="Back to the Newsstand">%s</a><div class="ear">No. %s<br>%s<br><b>%s</b><br>%s</div></div>'
        '<div class="flag"><div class="est">EST. 2026 · THE GARDEN · LEWISTON, ME</div><h1>The<br>Re-Up</h1><div class="motto">What the Garden needs, when it needs it</div></div>'
        '<div class="pc-band"><span>WANTED</span><span>FREE</span><span>FOR SALE</span></div>'
        '<div class="pc-teaser"><div class="kicker">%d ads today</div><b>%s</b></div><div class="pc-open">Read the ads ›</div>')
        % (SEAL, e(no), d.strftime("%a"), d.strftime("%b %-d"), d.strftime("%Y"), len(ads), e(ads[0].get("title") if ads else "Nothing wanted today")), " hardcover")
    body = ('<h2 class="ru-head">The Want Ads</h2>%s<p class="small">Tap an ad to answer it — have the agent handle it, do it yourself, or pass.</p>'
            '<div class="classifieds">%s</div>' % (('<p class="dek">%s</p>' % e(ed.get("intro"))) if ed.get("intro") else "", fb.listing_block(ads, "want")))
    pages = [front, page("The Want Ads", body)]
    fu = fb.followups_block(date)
    if fu:
        pages.append(page("Answered Ads", fu.replace("What happened to the jobs you approved", "What happened to the ads you answered")))
    pages.append(page("Back Page", (
        '<div class="gum"><span>THE RE-UP · CLASSIFIEDS DESK</span></div>'
        '<div class="pb-body"><a class="seal" href="/" aria-label="Back to the Newsstand" title="Back to the Newsstand">%s</a><h2 class="pb-title">The Re-Up</h2>'
        '<p>Set in type by Ganja from the agents\' nightly reports.<br>Answer an ad and the result shows here and in Discord.</p>'
        '%s<p class="pb-code">%s · No. %s</p><p><a href="../archive.html">Back issues ›</a> · <a href="/double-wide/">The Double Wide ›</a> · '
        '<a href="/">🏠 The Newsstand</a></p></div>')
        % (SEAL, back_codes("https://github.com/real-CAK3D/TheRe-Up", "TheRe-Up"), date, e(no)), " hardcover back"))
    return fb.book(pages, date=date, no=no, lists={"want": [{k: a.get(k) for k in KEYS} for a in ads]},
                   paper="The Re-Up", motto="What the Garden needs, when it needs it", gum="WANTED · FREE · FOR SALE · THE GARDEN",
                   price="PRICE: ONE FAVOR", delivered="SET BY GANJA", flap="The Re-Up · Classifieds from the Garden", body_class="pub-ru")


def main():
    ed = json.load(open(sys.argv[1]))
    dt.date.fromisoformat(ed["date"])
    os.makedirs(os.path.join(SITE, "issues"), exist_ok=True)
    open(os.path.join(SITE, "issues", ed["date"] + ".html"), "w").write(render(ed))
    print("rendered The Re-Up %s" % ed["date"])
    if "--no-build" not in sys.argv:
        import subprocess
        subprocess.run([sys.executable, os.path.join(ROOT, "build_re_up.py")], check=False)


if __name__ == "__main__":
    main()
