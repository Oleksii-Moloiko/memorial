(() => {
    const suppressFileTooltips = (root) => {
        root.querySelectorAll('input[type="file"]').forEach((input) => {
            if (input.closest(".admin-file-input-control")) {
                return;
            }

            // Let a label receive pointer events and open the native picker.
            // Hovering the native input can show a stale filename tooltip;
            // a whitespace title merely turns that tooltip into an empty box.
            const control = document.createElement("label");
            control.className = "admin-file-input-control";
            control.title = "";
            input.before(control);
            control.append(input);
        });
    };

    const init = () => suppressFileTooltips(document);

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    document.addEventListener("formset:added", (event) => {
        suppressFileTooltips(event.target);
    });
})();
