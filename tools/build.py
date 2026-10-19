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
# A form that redirects back with ?access=1 (e.g. the GHL form's redirect URL) grants access.
# ?access=0 clears it, for testing the gate again.
HEAD_GATE = """<script>(function(){var k='phm_playbooks_access',d=document.documentElement;try{if(/[?&]access=0\\b/.test(location.search))localStorage.removeItem(k);if(/[?&]access=1\\b/.test(location.search)){localStorage.setItem(k,'1');history.replaceState(null,'',location.pathname)}if(!localStorage.getItem(k))d.classList.add('locked')}catch(e){if(!/[?&]access=1\\b/.test(location.search))d.classList.add('locked')}})()</script>"""

GHL_SCRIPT = '<script src="https://link.msgsndr.com/js/form_embed.js"></script>'


def ghl_form(p):
    """GoHighLevel form as an inline embed. Set each form's redirect in GHL to
    /playbooks/<slug>/?access=1 so submitting unlocks the playbook."""
    fid, name = p["ghl_form_id"], html.escape(p["title"])
    return f"""<iframe src="https://api.leadconnectorhq.com/widget/form/{fid}" class="ghl-form"
    id="inline-{fid}" data-layout="{{'id':'INLINE'}}" data-trigger-type="alwaysShow" data-trigger-value=""
    data-activation-type="alwaysActivated" data-activation-value="" data-deactivation-type="neverDeactivate"
    data-deactivation-value="" data-form-name="{name}" data-height="280" data-layout-iframe-id="inline-{fid}"
    data-form-id="{fid}" data-cookie-consent="true" data-cookie-consent-provider="auto" title="{name}"></iframe>"""


def page(title, description, body, gated=False, extra=""):
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
{extra}
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
  <h2>Access the playbook</h2>
  <p>Enter your details to read it. You will also get new playbooks as they are published.</p>
{{forms}}
</dialog>"""
    forms = "\n".join(f'<div class="modal-form" data-slug="{p["slug"]}" hidden>{ghl_form(p)}</div>' for p in playbooks)
    body = body.replace("{forms}", forms)
    write("playbooks/index.html", page(
        "Playbooks | Paul Higgins Mentoring",
        "Free step-by-step playbooks for SaaS partners from Paul Higgins Mentoring.",
        body,
        extra=GHL_SCRIPT,
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
    <h2>Enter your details to read this playbook</h2>
    <p>Free access. You will also get new playbooks as they are published.</p>
    {ghl_form(p)}
  </div>
</section>
<section class="section pb-content">
  <div class="wrap narrow prose">
{content}
  </div>
</section>"""
    write(f"playbooks/{p['slug']}/index.html", page(
        f"{p['title']} Playbook | Paul Higgins Mentoring", p["summary"], body, gated=True, extra=GHL_SCRIPT,
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
