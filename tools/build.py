"""Builds the static site into public/ from src/.

Usage: python3 tools/build.py
"""
import datetime
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "public"

year = str(datetime.date.today().year)
header = (SRC / "partials" / "header.html").read_text()
footer = (SRC / "partials" / "footer.html").read_text().replace("{{year}}", year)
playbooks = json.loads((SRC / "playbooks.json").read_text())

# Runs before paint so gated content never flashes for visitors without access.
HEAD_GATE = """<script>try{if(!localStorage.getItem('phm_playbooks_access'))document.documentElement.classList.add('locked')}catch(e){document.documentElement.classList.add('locked')}</script>"""

GATE_FORM = """
<form class="gate-form" novalidate>
  <h2>{heading}</h2>
  <p>{blurb}</p>
  <label>First name<input type="text" name="name" autocomplete="given-name" required></label>
  <label>Email<input type="email" name="email" autocomplete="email" required></label>
  <input type="text" name="company" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
  <input type="hidden" name="playbook" value="{slug}">
  <button type="submit" class="btn">Get the playbook</button>
  <p class="form-error" role="alert" hidden></p>
</form>"""


def page(title, description, body, gated=False):
    e = html.escape
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{HEAD_GATE if gated else ""}
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
{header}
<main>
{body}
</main>
{footer}
<script src="/assets/gate.js" defer></script>
</body>
</html>
"""


def build_index():
    cards = "\n".join(
        f"""<a class="card" href="/playbooks/{p['slug']}/" data-slug="{p['slug']}">
  <h3>{html.escape(p['title'])}</h3>
  <p>{html.escape(p['summary'])}</p>
  <span class="card-cta">Read the playbook &rarr;</span>
</a>"""
        for p in playbooks
    )
    body = f"""<section class="hero">
  <div class="wrap narrow">
    <h1>The Paul Higgins Playbooks</h1>
    <p>Step-by-step playbooks for SaaS partners (e.g. Salesforce, Zoho, Microsoft, Monday, NetSuite, Acumatica) building revenue outside their vendor. Drawn from 200+ SaaS partners mentored and 700+ podcast interviews.</p>
  </div>
</section>
<section class="section">
  <div class="wrap narrow">
    <div class="card-grid">
{cards}
    </div>
  </div>
</section>
<dialog class="gate-modal" id="gate-modal">
  <button class="modal-close" type="button" aria-label="Close">&times;</button>
  {GATE_FORM.format(heading="Get free access to the playbooks", blurb="Enter your name and email to read every playbook and get new ones as they are published.", slug="")}
</dialog>"""
    write("playbooks/index.html", page(
        "Playbooks | Paul Higgins Mentoring",
        "Free step-by-step playbooks for SaaS partners from Paul Higgins Mentoring.",
        body,
    ))


def build_playbook(p):
    content = (SRC / "content" / f"{p['slug']}.html").read_text()
    body = f"""<section class="section pb-head">
  <div class="wrap narrow">
    <p class="back"><a href="/playbooks/">&larr; All playbooks</a></p>
    <h1>{html.escape(p['title'])} Playbook</h1>
    <p class="lede">{html.escape(p['summary'])}</p>
    <p class="meta">By Paul Higgins &middot; Updated {html.escape(p['updated'])}</p>
  </div>
</section>
<section class="section pb-gate">
  <div class="wrap narrow">
    {GATE_FORM.format(heading="Enter your details to read this playbook", blurb="Free access. You will also get new playbooks as they are published.", slug=p['slug'])}
  </div>
</section>
<section class="section pb-content">
  <div class="wrap narrow prose">
{content}
  </div>
</section>"""
    write(f"playbooks/{p['slug']}/index.html", page(
        f"{p['title']} Playbook | Paul Higgins Mentoring", p["summary"], body, gated=True,
    ))


def write(rel, text):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    build_index()
    for p in playbooks:
        build_playbook(p)
