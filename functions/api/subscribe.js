// Cloudflare Pages Function: POST /api/subscribe
// Forwards each signup as JSON to SUBSCRIBE_WEBHOOK_URL (a Zapier, Make or
// email-platform webhook) set in the Pages project's environment variables.

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function onRequestPost({ request, env }) {
  let data;
  try {
    data = await request.json();
  } catch {
    return json({ ok: false, error: 'Invalid request' }, 400);
  }

  // Honeypot: bots fill the hidden company field. Pretend success.
  if (data.company) return json({ ok: true });

  const name = String(data.name || '').trim().slice(0, 100);
  const email = String(data.email || '').trim().toLowerCase().slice(0, 254);
  if (!name || !EMAIL_RE.test(email)) {
    return json({ ok: false, error: 'Name and valid email required' }, 400);
  }

  const lead = {
    name,
    email,
    playbook: String(data.playbook || '').slice(0, 100),
    page: String(data.page || '').slice(0, 200),
    submitted_at: new Date().toISOString(),
    country: request.cf?.country || null,
  };

  if (!env.SUBSCRIBE_WEBHOOK_URL) {
    console.warn('SUBSCRIBE_WEBHOOK_URL not set; signup not forwarded', lead.email);
    return json({ ok: true, forwarded: false });
  }

  const res = await fetch(env.SUBSCRIBE_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(lead),
  });
  if (!res.ok) {
    console.error('Webhook failed', res.status);
    return json({ ok: false, error: 'Signup service unavailable' }, 502);
  }
  return json({ ok: true, forwarded: true });
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
