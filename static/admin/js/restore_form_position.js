(() => {
    const STORAGE_KEY =
        "memorial_admin_form_position:" + window.location.pathname;
    const form = document.querySelector(
        "#content-main form[id$='_form']"
    );

    let savedState = null;

    try {
        savedState = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
        sessionStorage.removeItem(STORAGE_KEY);
    } catch {
        // Відновлення позиції необов'язкове для роботи форми.
    }

    if (!form || !document.body.classList.contains("change-form")) {
        return;
    }

    const getSections = () =>
        Array.from(form.querySelectorAll("details"))
            .map((details) => ({
                details,
                heading: details.querySelector(
                    ":scope > summary [id]"
                ),
            }))
            .filter(({ heading }) => heading);

    const savePosition = () => {
        const state = {
            path: window.location.pathname,
            top: window.scrollY,
            time: Date.now(),
            sections: getSections().map(({ details, heading }) => ({
                id: heading.id,
                open: details.open,
            })),
        };

        try {
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch {
            // Збереження форми працює і без sessionStorage.
        }
    };

    form.addEventListener("submit", (event) => {
        const action = event.submitter?.name;

        if (action && action !== "_save" && action !== "_continue") {
            return;
        }

        savePosition();
    });

    // Запам'ятовуємо місце перед переходом у вкладене редагування.
    form.addEventListener("click", (event) => {
        const link = event.target.closest("a[href]");

        if (
            !link ||
            event.defaultPrevented ||
            event.button !== 0 ||
            event.ctrlKey ||
            event.metaKey ||
            event.shiftKey ||
            event.altKey ||
            link.hasAttribute("download") ||
            (link.target && link.target !== "_self")
        ) {
            return;
        }

        const destination = new URL(link.href, window.location.href);

        if (
            destination.origin === window.location.origin &&
            destination.pathname.startsWith("/admin/") &&
            destination.pathname !== window.location.pathname
        ) {
            savePosition();
        }
    });

    const hasErrors = () =>
        form.querySelector(
            ".errornote, .errorlist, [aria-invalid='true']"
        );

    if (
        !savedState ||
        savedState.path !== window.location.pathname ||
        Date.now() - savedState.time > 30 * 60 * 1000 ||
        !Number.isFinite(savedState.top) ||
        !Array.isArray(savedState.sections) ||
        hasErrors()
    ) {
        return;
    }

    const restore = async () => {
        if (document.fonts) {
            await document.fonts.ready;
        }

        if (hasErrors()) {
            return;
        }

        const sectionStates = new Map(
            savedState.sections.map((section) => [
                section.id,
                section.open,
            ])
        );

        getSections().forEach(({ details, heading }) => {
            if (sectionStates.has(heading.id)) {
                details.open = sectionStates.get(heading.id);
            }
        });

        requestAnimationFrame(() => {
            window.scrollTo({
                top: savedState.top,
                behavior: "instant",
            });
        });
    };

    if (document.readyState === "complete") {
        restore();
    } else {
        window.addEventListener("load", restore, { once: true });
    }
})();