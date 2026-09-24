(() => {
    "use strict";

    const initVideoUpload = () => {
        const videoInput = document.getElementById("id_video_file");
        const uploadIdInput = document.getElementById("id_video_upload_id");

        if (!videoInput || !uploadIdInput) {
            return;
        }

        const form = videoInput.closest("form");

        if (!form) {
            return;
        }

        const startUrl = videoInput.dataset.uploadStartUrl;
        const confirmUrl = videoInput.dataset.uploadConfirmUrl;
        const hasExistingVideo =
            videoInput.dataset.hasExistingVideo === "1";

        if (!startUrl || !confirmUrl) {
            return;
        }

        const MAX_SIZE = 300 * 1024 * 1024;
        const ALLOWED_EXTENSIONS = [".mp4", ".webm", ".mov"];

        const submitButtons = Array.from(form.elements).filter(
            (element) => element.matches('input[type="submit"], button[type="submit"]')
        );

        let activeRequest = null;
        let selectedFile = null;
        let uploadedFileName = "";

        let currentFileFingerprint = null;
        let verifiedFileFingerprint = null;
        let uploadInProgress = false;

        let uploadGeneration = 0;
        let verified = Boolean(uploadIdInput.value);

        // ---------------------------------------------------------
        // UI
        // ---------------------------------------------------------

        const statusContainer = document.createElement("div");
        statusContainer.className = "video-upload-status";

        const statusText = document.createElement("div");
        statusText.className = "video-upload-status__text";

        const progress = document.createElement("progress");
        progress.max = 100;
        progress.value = 0;
        progress.hidden = true;

        const actions = document.createElement("div");

        const cancelButton = document.createElement("button");
        cancelButton.type = "button";
        cancelButton.textContent = "Скасувати";
        cancelButton.hidden = true;

        const retryButton = document.createElement("button");
        retryButton.type = "button";
        retryButton.textContent = "Повторити";
        retryButton.hidden = true;

        actions.append(cancelButton, retryButton);

        statusContainer.append(
            statusText,
            progress,
            actions
        );

        const fieldRow = videoInput.closest(".form-row");
        const helpText = fieldRow?.querySelector(".help");
        const flexContainer = videoInput.closest(".flex-container");

        if (helpText) {
            helpText.insertAdjacentElement(
                "afterend",
                statusContainer
            );
        } else if (flexContainer) {
            flexContainer.insertAdjacentElement(
                "afterend",
                statusContainer
            );
        } else {
            videoInput.insertAdjacentElement(
                "afterend",
                statusContainer
            );
        }

        // ---------------------------------------------------------
        // Helpers
        // ---------------------------------------------------------

        const getCsrfToken = () => {
            const csrfInput = form.querySelector(
                'input[name="csrfmiddlewaretoken"]'
            );

            return csrfInput?.value || "";
        };

        const setSaveEnabled = (enabled) => {
            submitButtons.forEach((button) => {
                button.disabled = !enabled;
            });
        };

        const showIdle = () => {
            progress.hidden = true;
            cancelButton.hidden = true;
            retryButton.hidden = true;

            if (verified) {
                statusText.textContent = "Відео завантажено.";
                setSaveEnabled(true);
                return;
            }

            if (hasExistingVideo) {
                statusText.textContent =
                    "Поточне відео залишиться без змін.";
                setSaveEnabled(true);
                return;
            }

            statusText.textContent =
                "Оберіть відеофайл для завантаження.";

            setSaveEnabled(false);
        };

        const showStarting = () => {
            statusText.textContent =
                "Підготовка завантаження…";

            progress.hidden = false;
            progress.value = 0;

            cancelButton.hidden = false;
            retryButton.hidden = true;

            setSaveEnabled(false);
        };

        const showProgress = (percent) => {
            const rounded = Math.round(percent);

            progress.hidden = false;
            progress.value = rounded;

            statusText.textContent =
                `Завантаження: ${rounded}%`;

            cancelButton.hidden = false;
            retryButton.hidden = true;

            setSaveEnabled(false);
        };

        const showConfirming = () => {
            progress.hidden = false;
            progress.value = 100;

            statusText.textContent =
                "Перевіряємо завантажений файл…";

            cancelButton.hidden = true;
            retryButton.hidden = true;

            setSaveEnabled(false);
        };

        const showSuccess = () => {
            progress.hidden = false;
            progress.value = 100;

            statusText.textContent = uploadedFileName
                ? `Відео завантажено: ${uploadedFileName}`
                : "Відео завантажено.";

            cancelButton.hidden = true;
            retryButton.hidden = true;

            setSaveEnabled(true);
        };

        const showError = (message) => {
            progress.hidden = true;

            statusText.textContent =
                message || "Не вдалося завантажити відео.";

            cancelButton.hidden = true;
            retryButton.hidden = !selectedFile;

            setSaveEnabled(false);
        };

        const showCancelled = () => {
            progress.hidden = true;

            statusText.textContent =
                "Завантаження скасовано.";

            cancelButton.hidden = true;
            retryButton.hidden = !selectedFile;

            setSaveEnabled(false);
        };

        const getErrorMessage = async (response) => {
            try {
                const data = await response.json();

                if (data?.error) {
                    return data.error;
                }
            } catch {
                // Response was not JSON.
            }

            return "Сталася помилка під час завантаження.";
        };

        const validateFile = (file) => {
            if (!file) {
                return null;
            }

            const lowerName = file.name.toLowerCase();

            const extensionAllowed =
                ALLOWED_EXTENSIONS.some(
                    (extension) =>
                        lowerName.endsWith(extension)
                );

            if (!extensionAllowed) {
                return "Дозволені формати: MP4, WebM або MOV.";
            }

            if (file.size <= 0) {
                return "Відеофайл порожній.";
            }

            if (file.size > MAX_SIZE) {
                return "Розмір відео не повинен перевищувати 300 MB.";
            }

            return null;
        };

        const getFileFingerprint = (file) => {
            if (!file) {
                return null;
            }

            return [
                file.name,
                file.size,
                file.lastModified,
                file.type,
            ].join(":");
        };

        // ---------------------------------------------------------
        // Confirm
        // ---------------------------------------------------------

        const confirmUpload = async (
            uploadId,
            generation
        ) => {
            showConfirming();

            let response;

            try {
                response = await fetch(confirmUrl, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: JSON.stringify({
                        upload_id: uploadId,
                    }),
                });
            } catch {
                if (generation !== uploadGeneration) {
                    return;
                }

                showError(
                    "Не вдалося підтвердити завантаження."
                );
                return;
            }

            if (generation !== uploadGeneration) {
                return;
            }

            if (!response.ok) {
                uploadInProgress = false;

                showError(
                    await getErrorMessage(response)
                );
                return;
            }

            const data = await response.json();

            if (data.status !== "verified") {
                showError(
                    "Сервер не підтвердив завантаження відео."
                );
                return;
            }

            uploadIdInput.value = data.upload_id;
            verified = true;

            verifiedFileFingerprint =
                currentFileFingerprint;

            uploadInProgress = false;

            uploadedFileName = selectedFile?.name || "";

            videoInput.value = "";
            selectedFile = null;

            showSuccess();
        };

        // ---------------------------------------------------------
        // PUT directly to R2
        // ---------------------------------------------------------

        const putFile = (
            file,
            uploadId,
            uploadUrl,
            generation
        ) => {
            const xhr = new XMLHttpRequest();

            activeRequest = xhr;

            xhr.open("PUT", uploadUrl, true);

            if (file.type) {
                xhr.setRequestHeader(
                    "Content-Type",
                    file.type
                );
            }

            xhr.upload.addEventListener(
                "progress",
                (event) => {
                    if (
                        generation !== uploadGeneration ||
                        !event.lengthComputable
                    ) {
                        return;
                    }

                    const percent =
                        (event.loaded / event.total) * 100;

                    showProgress(percent);
                }
            );

            xhr.addEventListener("load", () => {
                if (generation !== uploadGeneration) {
                    return;
                }

                activeRequest = null;

                if (xhr.status < 200 || xhr.status >= 300) {
                    showError(
                        `R2 повернув помилку ${xhr.status}.`
                    );
                    return;
                }

                confirmUpload(
                    uploadId,
                    generation
                );
            });

            xhr.addEventListener("error", () => {
                if (generation !== uploadGeneration) {
                    return;
                }

                activeRequest = null;
                uploadInProgress = false;

                showError(
                    "Не вдалося завантажити файл у R2. "
                    + "Перевірте з’єднання та CORS."
                );
            });

            xhr.addEventListener("abort", () => {
                if (generation !== uploadGeneration) {
                    return;
                }

                activeRequest = null;
                uploadInProgress = false;
                showCancelled();
            });

            xhr.send(file);
        };

        // ---------------------------------------------------------
        // Start
        // ---------------------------------------------------------

        const startUpload = async (
            file,
            generation
        ) => {
            uploadInProgress = true;

            showStarting();

            let response;

            try {
                response = await fetch(startUrl, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: JSON.stringify({
                        name: file.name,
                        size: file.size,
                        content_type: file.type || "",
                    }),
                });
            } catch {
                if (generation !== uploadGeneration) {
                    return;
                }

                uploadInProgress = false;

                showError(
                    "Не вдалося почати завантаження."
                );
                return;
            }

            if (generation !== uploadGeneration) {
                return;
            }

            if (!response.ok) {
                uploadInProgress = false;

                showError(
                    await getErrorMessage(response)
                );
                return;
            }

            const data = await response.json();

            if (!data.upload_id || !data.upload_url) {
                uploadInProgress = false;

                showError(
                    "Сервер повернув некоректні дані завантаження."
                );
                return;
            }

            putFile(
                file,
                data.upload_id,
                data.upload_url,
                generation
            );
        };

        // ---------------------------------------------------------
        // Events
        // ---------------------------------------------------------

        videoInput.addEventListener("change", () => {
            const newFile =
                videoInput.files?.[0] || null;

            if (!newFile) {
                return;
            }

            const newFingerprint =
                getFileFingerprint(newFile);

            /*
             * Той самий файл уже зараз завантажується.
             *
             * Нічого не скасовуємо і не запускаємо заново.
             */
            if (
                uploadInProgress
                && newFingerprint === currentFileFingerprint
            ) {
                return;
            }

            /*
             * Цей самий файл уже успішно завантажений.
             *
             * Очищаємо native file input, щоб файл
             * випадково не пішов через Django при Save,
             * але зберігаємо verified upload_id.
             */
            if (
                verified
                && newFingerprint === verifiedFileFingerprint
            ) {
                videoInput.value = "";
                showSuccess();
                return;
            }

            /*
             * Це справді інший файл.
             * Старий upload більше не повинен бути
             * пов'язаний із формою.
             */
            uploadGeneration += 1;

            if (activeRequest) {
                activeRequest.abort();
                activeRequest = null;
            }

            uploadIdInput.value = "";
            verified = false;

            selectedFile = newFile;
            currentFileFingerprint = newFingerprint;

            const validationError =
                validateFile(selectedFile);

            if (validationError) {
                uploadInProgress = false;
                showError(validationError);
                return;
            }

            startUpload(
                selectedFile,
                uploadGeneration
            );
        });

        cancelButton.addEventListener("click", () => {
            if (activeRequest) {
                activeRequest.abort();
            }
        });

        retryButton.addEventListener("click", () => {
            if (!selectedFile) {
                return;
            }

            uploadGeneration += 1;

            uploadIdInput.value = "";
            verified = false;

            startUpload(
                selectedFile,
                uploadGeneration
            );
        });

        // Якщо форма повернулась після validation error,
        // verified upload_id вже буде в hidden field.
                showIdle();
    };

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initVideoUpload
        );
    } else {
        initVideoUpload();
    }
})();
