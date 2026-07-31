
(() => {
  const qs = new URLSearchParams(location.search);
  const mode = qs.get('view') === 'wireframe' ? 'wireframe' : 'design';
  document.body.classList.toggle('wireframe', mode === 'wireframe');
  document.querySelector(`.mode-${mode}`)?.classList.add('active');

  const navigationBase = location.protocol === 'about:' ? 'https://prototype.local/' : location.href;

  document.querySelectorAll('[data-preserve-query]').forEach(link => {
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('http')) return;
    const url = new URL(href, navigationBase);
    url.searchParams.set('view', mode);
    link.setAttribute('href', url.pathname.split('/').pop() + url.search);
  });

  const navToggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.primary-nav');
  navToggle?.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(open));
  });

  const gridToggle = document.querySelector('.grid-toggle');
  gridToggle?.addEventListener('click', () => {
    const active = document.body.classList.toggle('grid-overlay');
    gridToggle.setAttribute('aria-pressed', String(active));
  });

  document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());

  const toast = document.querySelector('.toast');
  const showToast = message => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(window.__toastTimer);
    window.__toastTimer = setTimeout(() => toast.classList.remove('show'), 2400);
  };

  document.querySelectorAll('.demo-action').forEach(el => el.addEventListener('click', e => {
    e.preventDefault();
    showToast('Демонстраційна дія: додайте перевірене посилання або файл.');
  }));

  const form = document.querySelector('.demo-form');
  form?.addEventListener('submit', e => {
    e.preventDefault();
    showToast('Демо: повідомлення передано б на ручну модерацію.');
    form.reset();
    const counter = form.querySelector('.counter');
    if (counter) counter.textContent = '0 / 500';
  });

  const textarea = document.querySelector('textarea[maxlength]');
  textarea?.addEventListener('input', () => {
    const counter = textarea.parentElement.querySelector('.counter');
    if (counter) counter.textContent = `${textarea.value.length} / ${textarea.maxLength}`;
  });

  document.querySelectorAll('.filter-chip').forEach(btn => btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-chip').forEach(x => x.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.dataset.filter;
    document.querySelectorAll('.gallery-card').forEach(card => card.classList.toggle('is-hidden', filter !== 'all' && card.dataset.category !== filter));
  }));

  document.querySelectorAll('.media-filter').forEach(btn => btn.addEventListener('click', () => {
    document.querySelectorAll('.media-filter').forEach(x => x.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.dataset.mediaFilter;
    document.querySelectorAll('.article-row').forEach(row => row.classList.toggle('is-hidden', filter !== 'all' && row.dataset.mediaCategory !== filter));
  }));

  const dialog = document.querySelector('.gallery-dialog');
  document.querySelectorAll('.gallery-open').forEach(btn => btn.addEventListener('click', () => {
    if (!dialog) return;
    dialog.querySelector('.dialog-caption').textContent = btn.dataset.caption || '';
    dialog.showModal();
  }));
  dialog?.querySelector('.dialog-close')?.addEventListener('click', () => dialog.close());
  dialog?.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
})();
