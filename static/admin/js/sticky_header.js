(() => {
    const header = document.getElementById("header");
    if (!header || document.body.classList.contains("login")) return;

    const navigation = header.nextElementSibling;
    if (!navigation || navigation.tagName !== "NAV") return;

    const toolbar = document.createElement("div");
    toolbar.className = "admin-sticky-header";
    header.before(toolbar);
    toolbar.append(header, navigation);

    const form = document.querySelector("#content-main form[id$='_form']");
    if (form && document.body.classList.contains("change-form")) {
        const actions = document.createElement("div");
        actions.className = "admin-header-actions";
        const actionNames = new Set();
        // Move the original controls so permissions, names and event handlers
        // remain intact. Explicit form ownership retains native validation.
        form.querySelectorAll(".submit-row input[type='submit']").forEach((button) => {
            // Django's save_on_top renders the same actions twice.
            if (actionNames.has(button.name)) {
                button.remove();
                return;
            }
            actionNames.add(button.name);
            button.setAttribute("form", form.id);
            actions.append(button);
        });
        if (actions.childElementCount) navigation.append(actions);
        form.querySelectorAll(".submit-row").forEach((row) => {
            if (!row.childElementCount) row.remove();
        });
    }

    const updateHeight = () => {
        document.documentElement.style.setProperty(
            "--admin-sticky-header-height", `${toolbar.getBoundingClientRect().height}px`
        );
    };
    new ResizeObserver(updateHeight).observe(toolbar);
    updateHeight();
})();
