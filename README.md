# Paul Higgins Playbooks

Static playbook library hosted on Cloudflare Pages. Visitors see the list at `/playbooks/`, enter name and email, then read the playbook.

## Layout

- `src/playbooks.json` lists each playbook (slug, title, summary, source Google Doc).
- `src/content/<slug>.html` is the playbook body, converted from the Google Doc.
- `src/partials/header.html` and `footer.html` are shared on every page.
- `tools/build.py` writes the pages into `public/`. Run `python3 tools/build.py` after any change in `src/` and commit `public/`.
- `tools/gdoc2html.py <docs-api-json> <tabId>` converts a Google Docs API export to HTML.
- `functions/api/subscribe.js` receives signups and forwards them to `SUBSCRIBE_WEBHOOK_URL`.

## Cloudflare Pages settings

- Build command: none
- Build output directory: `public`
- Environment variable: `SUBSCRIBE_WEBHOOK_URL` (Zapier, Make or email-platform webhook that adds the contact)

## Adding a playbook

1. Export the Google Doc via the Docs API and run `tools/gdoc2html.py` to create `src/content/<slug>.html`.
2. Add an entry to `src/playbooks.json`.
3. Run `python3 tools/build.py`, commit and push. Cloudflare deploys automatically.

Access is stored in the visitor's browser, so it is a soft gate, the same model as jamesschramko.com/playbooks.
