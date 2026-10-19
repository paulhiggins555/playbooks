(function () {
  var KEY = 'phm_playbooks_access';

  // ?access=0 forgets access so the gate can be tested again.
  if (/[?&]access=0\b/.test(location.search)) {
    try { localStorage.removeItem(KEY); } catch (e) { /* storage blocked: nothing stored */ }
  }

  function hasAccess() {
    try { return !!localStorage.getItem(KEY); } catch (e) { return false; }
  }

  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = document.body.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Listing page: a card opens that playbook's GHL form unless the visitor already has access.
  // The GHL form redirects to the playbook with ?access=1, which unlocks it.
  var modal = document.getElementById('gate-modal');
  if (!modal) return;
  document.querySelectorAll('.card[data-slug]').forEach(function (card) {
    card.addEventListener('click', function (ev) {
      if (hasAccess() || !modal.showModal) return;
      ev.preventDefault();
      modal.querySelectorAll('.modal-form').forEach(function (f) {
        f.hidden = f.dataset.slug !== card.dataset.slug;
      });
      modal.showModal();
    });
  });
  modal.querySelector('.modal-close').addEventListener('click', function () { modal.close(); });
  modal.addEventListener('click', function (ev) { if (ev.target === modal) modal.close(); });
})();
