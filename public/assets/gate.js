(function () {
  var KEY = 'phm_playbooks_access';

  function hasAccess() {
    try { return !!localStorage.getItem(KEY); } catch (e) { return false; }
  }
  function grantAccess(email) {
    try { localStorage.setItem(KEY, email || '1'); } catch (e) { /* private mode: access lasts this page view */ }
    document.documentElement.classList.remove('locked');
  }

  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = document.body.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  var modal = document.getElementById('gate-modal');
  var pendingUrl = null;

  // Listing page: cards open the opt-in unless the visitor already has access.
  document.querySelectorAll('.card[data-slug]').forEach(function (card) {
    card.addEventListener('click', function (ev) {
      if (hasAccess() || !modal) return;
      ev.preventDefault();
      pendingUrl = card.getAttribute('href');
      modal.querySelector('input[name="playbook"]').value = card.dataset.slug;
      if (modal.showModal) modal.showModal(); else window.location = pendingUrl;
    });
  });
  if (modal) {
    modal.querySelector('.modal-close').addEventListener('click', function () { modal.close(); });
    modal.addEventListener('click', function (ev) { if (ev.target === modal) modal.close(); });
  }

  document.querySelectorAll('.gate-form').forEach(function (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var err = form.querySelector('.form-error');
      var name = form.name.value.trim();
      var email = form.email.value.trim();
      if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        err.textContent = 'Enter your first name and a valid email.';
        err.hidden = false;
        return;
      }
      err.hidden = true;
      var btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.textContent = 'One moment...';

      var done = function () {
        grantAccess(email);
        if (pendingUrl) window.location = pendingUrl;
        else window.scrollTo(0, 0);
      };
      fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name,
          email: email,
          playbook: form.playbook.value,
          company: form.company.value,
          page: window.location.pathname
        })
      }).then(done, done); // never lock a reader out because the signup call failed
    });
  });
})();
