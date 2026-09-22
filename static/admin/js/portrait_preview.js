(() => {
    const init = () => {
        const input = document.getElementById("id_portrait");
        const preview = document.querySelector(
            ".field-large_portrait_preview .readonly"
        );
        if (!input || !preview) return;

        const clear = document.getElementById("portrait-clear_id");
        const original = Array.from(preview.childNodes, node => node.cloneNode(true));
        let objectUrl = null;

        const release = () => {
            if (objectUrl) URL.revokeObjectURL(objectUrl);
            objectUrl = null;
        };

        const update = () => {
            release();
            const file = input.files?.[0];
            if (file) {
                const image = document.createElement("img");
                image.alt = "Попередній перегляд вибраного портрета";
                image.style.cssText = "max-width:min(360px, 100%);max-height:420px;object-fit:contain;border-radius:8px;";
                image.onerror = () => {
                    if (preview.contains(image)) {
                        preview.textContent = "Не вдалося відкрити вибране зображення.";
                    }
                };
                objectUrl = URL.createObjectURL(file);
                image.src = objectUrl;
                preview.replaceChildren(image);
            } else if (clear?.checked) {
                preview.textContent = "Портрет буде видалено після збереження.";
            } else {
                preview.replaceChildren(...original.map(node => node.cloneNode(true)));
            }
        };

        input.addEventListener("change", update);
        clear?.addEventListener("change", update);
        input.form?.addEventListener("reset", () => setTimeout(update, 0));
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
