(() => {
    let counter = 0;

    const init = (root) => {
        root.querySelectorAll('input[type="file"]').forEach((input) => {
            // Порожній шаблон Django обробимо після додавання рядка.
            if (
                input.closest(".empty-form") ||
                input.closest(".admin-file-input-control")
            ) {
                return;
            }

            const existingLink = input
                .closest(".file-upload")
                ?.querySelector("a[href]");

            const existingName =
                input.dataset.existingFileName ||
                existingLink?.textContent.trim().split("/").pop() ||
                "";

            const clear = input.form?.elements.namedItem(
                `${input.name}-clear`
            );

            const isVideoUpload = Boolean(input.dataset.uploadStartUrl);

            const control = document.createElement("label");
            control.className = "admin-file-input-control";

            const button = document.createElement("span");
            button.className = "admin-file-input-button";
            button.setAttribute("aria-hidden", "true");

            const name = document.createElement("span");
            name.className = "admin-file-input-name";
            name.setAttribute("aria-hidden", "true");

            const status = document.createElement("span");
            status.className = "admin-file-input-status";
            status.id = `admin-file-status-${++counter}`;
            status.setAttribute("role", "status");

            const wrapper = document.createElement("span");
            wrapper.className = "admin-file-input-wrapper";

            input.before(wrapper);
            wrapper.append(control, status);
            control.append(input, button, name);

            input.setAttribute(
                "aria-describedby",
                [input.getAttribute("aria-describedby"), status.id]
                    .filter(Boolean)
                    .join(" ")
            );

            const update = () => {
                const file = input.files?.[0];
                let state = "idle";
                let filename = existingName;
                let message = existingName
                    ? "✓ Файл збережено."
                    : "Файл ще не вибрано.";

                if (isVideoUpload) {
                    state = input.dataset.uploadState || "idle";
                    filename =
                        input.dataset.uploadFileName ||
                        file?.name ||
                        existingName;

                    if (state === "success") {
                        message = input.dataset.uploadFileName
                            ? "✓ Відео завантажено. Збережіть форму."
                            : existingName
                                ? "✓ Поточне відео збережено."
                                : "✓ Відео завантажено. Збережіть форму.";
                    } else if (state === "uploading") {
                        message = "Відео завантажується та перевіряється…";
                    } else if (state === "error") {
                        message = "Помилка завантаження — дивіться пояснення нижче.";
                    } else if (state === "cancelled") {
                        message = "Завантаження скасовано.";
                    } else if (existingName) {
                        state = "success";
                    }
                } else if (file) {
                    state = "selected";
                    filename = file.name;
                    message = "Файл вибрано. Щоб завантажити його, збережіть форму.";
                } else if (clear?.checked) {
                    state = "clear";
                    message = "Файл буде видалено після збереження.";
                } else if (existingName) {
                    state = "success";
                }

                // Помилка поля має пріоритет над зеленою позначкою.
                if (input.getAttribute("aria-invalid") === "true") {
                    state = "error";
                    message = "Поле містить помилку — перевірте повідомлення біля нього.";
                }

                control.dataset.state = state;
                control.classList.toggle("is-disabled", input.disabled);
                button.textContent =
                    filename || state === "success"
                        ? "Замінити файл"
                        : "Обрати файл";
                name.textContent = filename || (
                    state === "success" ? "Завантажений файл" : ""
                );

                if (status.textContent !== message) {
                    status.textContent = message;
                }
            };

            // Чекаємо, доки інші обробники оновлять прев'ю та стан відео.
            const scheduleUpdate = () => queueMicrotask(update);

            input.addEventListener("change", scheduleUpdate);
            input.addEventListener("admin:upload-state", update);
            clear?.addEventListener("change", scheduleUpdate);
            input.form?.addEventListener("reset", () => {
                setTimeout(update, 0);
            });

            update();
        });
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => init(document));
    } else {
        init(document);
    }

    document.addEventListener("formset:added", (event) => {
        init(event.target);
    });
})();