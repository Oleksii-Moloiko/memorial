/* The Memorial menu replaces Django's table-based navigation and quick filter. */
'use strict';
(() => {
    const toggle = document.getElementById('toggle-nav-sidebar');
    const sidebar = document.getElementById('nav-sidebar');
    const main = document.getElementById('main');
    if (!toggle || !sidebar || !main) return;

    const mobile = window.matchMedia('(max-width: 767px)');
    const storageKey = 'django.admin.navSidebarIsOpen';
    let desktopOpen = true;
    try {
        desktopOpen = localStorage.getItem(storageKey) !== 'false';
    } catch (_) { /* Navigation still works when storage is unavailable. */ }

    function setOpen(open) {
        main.classList.toggle('shifted', open);
        toggle.setAttribute('aria-expanded', String(open));
        sidebar.setAttribute('aria-expanded', String(open));
        sidebar.inert = !open;
    }

    function closeMobile() {
        if (mobile.matches) setOpen(false);
    }

    setOpen(!mobile.matches && desktopOpen);
    toggle.addEventListener('click', () => {
        const open = !main.classList.contains('shifted');
        setOpen(open);
        if (!mobile.matches) {
            desktopOpen = open;
            try { localStorage.setItem(storageKey, String(open)); } catch (_) { /* Optional. */ }
        }
    });
    sidebar.addEventListener('click', event => {
        if (event.target.closest('a[href]')) closeMobile();
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && mobile.matches && main.classList.contains('shifted')) {
            closeMobile();
            toggle.focus();
        }
    });
    document.addEventListener('click', event => {
        if (!sidebar.contains(event.target) && !toggle.contains(event.target)) closeMobile();
    });
    mobile.addEventListener('change', () => setOpen(!mobile.matches && desktopOpen));
    // A back/forward-cache restore must not reopen the mobile drawer.
    window.addEventListener('pageshow', closeMobile);
})();
