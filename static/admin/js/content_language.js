(() => {
    const STORAGE_KEY = "memorial_admin_content_language";
    const DEFAULT_LANGUAGE = "uk";
    const SUPPORTED_LANGUAGES = ["uk", "en"];

    const switcher = document.querySelector(
        "[data-admin-language-switcher]"
    );

    if (!switcher) {
        return;
    }

    const buttons = switcher.querySelectorAll(
        "[data-admin-content-language]"
    );

    const getStoredLanguage = () => {
        const storedLanguage = localStorage.getItem(STORAGE_KEY);

        if (SUPPORTED_LANGUAGES.includes(storedLanguage)) {
            return storedLanguage;
        }

        return DEFAULT_LANGUAGE;
    };

    const getFieldLanguage = (element) => {
        for (const className of element.classList) {
            if (!className.startsWith("field-")) {
                continue;
            }

            if (className.endsWith("_uk")) {
                return "uk";
            }

            if (className.endsWith("_en")) {
                return "en";
            }
        }

        return null;
    };

    const updateFields = (language) => {
        const fieldContainers = document.querySelectorAll(
            ".form-row, .fieldBox, .inline-related td, .inline-related th"
        );

        fieldContainers.forEach((fieldContainer) => {
            const fieldLanguage = getFieldLanguage(fieldContainer);

            if (!fieldLanguage) {
                return;
            }

            fieldContainer.hidden = fieldLanguage !== language;
        });
    };

    const updateButtons = (language) => {
        buttons.forEach((button) => {
            const buttonLanguage =
                button.dataset.adminContentLanguage;
            const isActive = buttonLanguage === language;
            const label = buttonLanguage === "uk" ? "UA" : "EN";

            const errorCount = invalidFields.filter(
                (field) => getInputLanguage(field) === buttonLanguage
            ).length;

            button.textContent = errorCount
                ? `${label} (${errorCount})`
                : label;

            button.classList.toggle("is-active", isActive);
            button.classList.toggle("has-errors", errorCount > 0);

            button.setAttribute("aria-pressed", String(isActive));
            button.setAttribute(
                "aria-label",
                errorCount
                    ? `${label}: полів із помилками — ${errorCount}`
                    : label
            );
        });
    };

    const setLanguage = (language) => {
        if (!SUPPORTED_LANGUAGES.includes(language)) {
            language = DEFAULT_LANGUAGE;
        }

        localStorage.setItem(STORAGE_KEY, language);

        document.documentElement.dataset.adminContentLanguage =
            language;

        updateButtons(language);
        updateFields(language);
    };

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            setLanguage(
                button.dataset.adminContentLanguage
            );
        });
    });

    const invalidFields = Array.from(
        document.querySelectorAll(
            'input[aria-invalid="true"], ' +
            'select[aria-invalid="true"], ' +
            'textarea[aria-invalid="true"]'
        )
    );

    const getInputLanguage = (field) => {
        for (const language of SUPPORTED_LANGUAGES) {
            if (field.name.endsWith(`_${language}`)) {
                return language;
            }
        }

        return null;
    };

    // Якщо помилки є в обох мовах, першою відкриваємо українську.
    const errorLanguage = SUPPORTED_LANGUAGES.find((language) =>
        invalidFields.some(
            (field) => getInputLanguage(field) === language
        )
    );

    const initialLanguage = errorLanguage || getStoredLanguage();
    setLanguage(initialLanguage);

    const firstInvalidField = invalidFields.find((field) => {
        const language = getInputLanguage(field);
        return !language || language === initialLanguage;
    });

    const revealError = (field) => {
        const language = getInputLanguage(field);

        if (language) {
            setLanguage(language);
        }

        let parent = field.parentElement;

        while (parent) {
            if (parent.tagName === "DETAILS") {
                parent.open = true;
            }

            parent = parent.parentElement;
        }

        requestAnimationFrame(() => {
            field.scrollIntoView({
                block: "center",
                behavior: "instant",
            });
            field.focus({ preventScroll: true });
        });
    };

    const errorNote = document.querySelector(".errornote");

    if (errorNote) {
        const languageNames = {
            uk: "української",
            en: "англійської",
        };

        SUPPORTED_LANGUAGES.forEach((language) => {
            const fields = invalidFields.filter(
                (field) => getInputLanguage(field) === language
            );

            if (!fields.length) {
                return;
            }

            const firstField = fields[0];
            const link = document.createElement("a");

            link.className = "admin-language-error-link";
            link.href = `#${firstField.id}`;
            link.textContent =
                `Помилки ${languageNames[language]} версії ` +
                `(${fields.length}) — перейти до поля`;

            link.addEventListener("click", (event) => {
                event.preventDefault();
                revealError(firstField);
            });

            errorNote.appendChild(link);
        });
    }

    if (firstInvalidField) {
        revealError(firstInvalidField);
    }
})();