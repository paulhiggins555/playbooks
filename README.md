# Paul Higgins Playbooks

Static playbook library hosted on Cloudflare Pages. Visitors see the list at `/playbooks/`, enter name and email, then read the playbook.

## Layout

- `src/playbooks.json` lists each playbook (slug, title, summary, source Google Doc).
- `src/content/<slug>.html` is the playbook body, converted from the Google Doc.
- `src/partials/header.html` and `footer.html` are shared on every page.
- `tools/build.py` writes the pages into `public/`. Run `python3 tools/build.py` after any change in `src/` and commit `public/`.
- `tools/gdoc2html.py <docs-api-json> <tabId>` converts a Google Docs API export to HTML.
- Each playbook's `ghl_form_id` in `src/playbooks.json` is its GoHighLevel form. In GHL, set the form's redirect to `/playbooks/<slug>/?access=1`; that unlocks the playbook in the reader's browser.

## Cloudflare Pages settings

- Build command: none
- Build output directory: `public`

## Adding a playbook

1. Export the Google Doc via the Docs API and run `tools/gdoc2html.py` to create `src/content/<slug>.html`.
2. Create a GHL form, then add an entry to `src/playbooks.json` with its form ID.
3. Run `python3 tools/build.py`, commit and push. Cloudflare deploys automatically.

Access is stored in the visitor's browser, so it is a soft gate, the same model as jamesschramko.com/playbooks.
