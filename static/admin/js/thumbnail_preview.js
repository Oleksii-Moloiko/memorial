(() => {
    const init = () => {
        const input = document.getElementById("id_thumbnail");
        const preview = document.querySelector(
            ".field-large_thumbnail_preview .readonly"
        );

        if (!input || !preview) return;

        const clear = document.getElementById("thumbnail-clear_id");
        const original = Array.from(
            preview.childNodes,
            (node) => node.cloneNode(true)
        );

        preview.setAttribute("aria-live", "polite");

        let objectUrl = null;

        const release = () => {
            if (objectUrl) {
                URL.revokeObjectURL(objectUrl);
                objectUrl = null;
            }
        };

        const update = () => {
            release();

            const file = input.files?.[0];

            if (file) {
                const image = document.createElement("img");

                image.alt = "Попередній перегляд вибраної обкладинки";
                image.style.cssText =
                    "display:block;width:100%;max-width:500px;" +
                    "height:auto;max-height:280px;object-fit:contain;";

                image.onerror = () => {
                    if (preview.contains(image)) {
                        preview.textContent =
                            "Не вдалося відкрити вибране зображення.";
                    }
                };

                const note = document.createElement("p");
                note.textContent =
                    "Попередній перегляд. Щоб зберегти обкладинку, збережіть форму.";

                objectUrl = URL.createObjectURL(file);
                image.src = objectUrl;

                preview.replaceChildren(image, note);
            } else if (clear?.checked) {
                preview.textContent =
                    "Обкладинку буде видалено після збереження.";
            } else {
                preview.replaceChildren(
                    ...original.map((node) => node.cloneNode(true))
                );
            }
        };

        input.addEventListener("change", () => {
            if (input.files?.length && clear) {
                clear.checked = false;
            }

            update();
        });

        clear?.addEventListener("change", () => {
            if (clear.checked) {
                input.value = "";
            }

            update();
        });

        input.form?.addEventListener("reset", () => {
            setTimeout(update, 0);
        });
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();