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
            const isActive =
                button.dataset.adminContentLanguage === language;

            button.classList.toggle("is-active", isActive);
            button.setAttribute(
                "aria-pressed",
                isActive ? "true" : "false"
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

    setLanguage(getStoredLanguage());
})();