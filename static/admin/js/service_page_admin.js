(() => {
    const addLabels = {
        awards: "Додати нагороду",
        quotes: "Додати цитату",
        mentions: "Додати посилання",
    };

    document
        .querySelectorAll(".js-inline-admin-formset")
        .forEach((inlineGroup) => {
            const prefix = inlineGroup.id.replace(/-group$/, "");
            const addLabel = addLabels[prefix];

            if (!addLabel) {
                return;
            }

            const rawInlineData =
                inlineGroup.dataset.inlineFormset;

            if (!rawInlineData) {
                return;
            }

            try {
                const inlineData = JSON.parse(rawInlineData);

                inlineData.options.addText = addLabel;

                inlineGroup.dataset.inlineFormset =
                    JSON.stringify(inlineData);
            } catch {
                // Якщо Django змінить формат даних,
                // стандартна кнопка просто залишиться без змін.
            }
        });
})();