const initPhotoCropper = () => {
  const editor = document.querySelector("[data-photo-crop-editor]");

  if (!editor) {
    return;
  }

  const imageInput = document.querySelector("#id_image");
  const xInput = document.querySelector("#id_preview_focus_x");
  const yInput = document.querySelector("#id_preview_focus_y");
  const stages = Array.from(editor.querySelectorAll("[data-crop-stage]"));
  const images = Array.from(editor.querySelectorAll("[data-crop-image]"));
  const resetButton = editor.querySelector("[data-crop-reset]");
  const positionOutput = editor.querySelector("[data-crop-position]");
  const emptyState = editor.querySelector("[data-crop-empty]");
  const hint = editor.querySelector("[data-crop-hint]");

  if (!xInput || !yInput || !stages.length || !images.length) {
    return;
  }

  const clamp = (value, min = 0, max = 100) =>
    Math.min(Math.max(value, min), max);

  const readPercent = (input) => {
    const value = Number.parseFloat(input.value);
    return Number.isFinite(value) ? clamp(value) : 50;
  };

  let focusX = readPercent(xInput);
  let focusY = readPercent(yInput);
  let objectUrl = null;
  let dragState = null;

  const getExistingImageUrl = () => {
    const configuredUrl = (editor.dataset.imageUrl || "").trim();

    if (configuredUrl) {
      return configuredUrl;
    }

    // Django's ClearableFileInput already renders a link to the current file
    // on the change form. Use it as a fallback so saved photos are shown
    // immediately even if the readonly editor did not receive the object URL.
    const fieldContainer =
      imageInput?.closest(".form-row") ||
      imageInput?.closest(".field-image") ||
      imageInput?.parentElement;
    const currentImageLink = fieldContainer?.querySelector(
      ".file-upload a[href], a[href]"
    );

    return currentImageLink?.href || "";
  };

  const updateUI = () => {
    const position = `${focusX}% ${focusY}%`;

    images.forEach((image) => {
      image.style.objectPosition = position;
    });

    xInput.value = String(Math.round(focusX));
    yInput.value = String(Math.round(focusY));

    if (positionOutput) {
      positionOutput.textContent = `${Math.round(focusX)}% × ${Math.round(focusY)}%`;
    }
  };

  const setImage = (src) => {
    const hasImage = Boolean(src);

    images.forEach((image) => {
      if (hasImage) {
        image.src = src;
      } else {
        image.removeAttribute("src");
      }
    });

    stages.forEach((stage) => {
      stage.classList.toggle("is-empty", !hasImage);
    });

    if (emptyState) {
      emptyState.hidden = hasImage;
    }

    if (hint) {
      hint.hidden = !hasImage;
    }
  };

  const moveFocus = (deltaX, deltaY, stage) => {
    const rect = stage.getBoundingClientRect();

    if (!rect.width || !rect.height) {
      return;
    }

    // Moving the photo left reveals more of its right side, matching Telegram-like crop UX.
    focusX = clamp(focusX - (deltaX / rect.width) * 100);
    focusY = clamp(focusY - (deltaY / rect.height) * 100);
    updateUI();
  };

  stages.forEach((stage) => {
    stage.addEventListener("pointerdown", (event) => {
      if (stage.classList.contains("is-empty")) {
        return;
      }

      dragState = {
        stage,
        pointerId: event.pointerId,
        x: event.clientX,
        y: event.clientY,
      };

      stage.setPointerCapture(event.pointerId);
      stage.classList.add("is-dragging");
      hint?.setAttribute("hidden", "");
      event.preventDefault();
    });

    stage.addEventListener("pointermove", (event) => {
      if (!dragState || dragState.pointerId !== event.pointerId) {
        return;
      }

      const deltaX = event.clientX - dragState.x;
      const deltaY = event.clientY - dragState.y;

      moveFocus(deltaX, deltaY, dragState.stage);

      dragState.x = event.clientX;
      dragState.y = event.clientY;
    });

    const endDrag = (event) => {
      if (!dragState || dragState.pointerId !== event.pointerId) {
        return;
      }

      dragState.stage.classList.remove("is-dragging");
      dragState = null;
    };

    stage.addEventListener("pointerup", endDrag);
    stage.addEventListener("pointercancel", endDrag);

    stage.addEventListener("keydown", (event) => {
      if (stage.classList.contains("is-empty")) {
        return;
      }

      const step = event.shiftKey ? 5 : 1;
      let handled = true;

      switch (event.key) {
        case "ArrowLeft":
          focusX = clamp(focusX - step);
          break;
        case "ArrowRight":
          focusX = clamp(focusX + step);
          break;
        case "ArrowUp":
          focusY = clamp(focusY - step);
          break;
        case "ArrowDown":
          focusY = clamp(focusY + step);
          break;
        default:
          handled = false;
      }

      if (handled) {
        updateUI();
        event.preventDefault();
      }
    });
  });

  resetButton?.addEventListener("click", () => {
    focusX = 50;
    focusY = 50;
    updateUI();
  });

  imageInput?.addEventListener("change", () => {
    const file = imageInput.files?.[0];

    if (objectUrl) {
      URL.revokeObjectURL(objectUrl);
      objectUrl = null;
    }

    if (!file) {
      setImage(getExistingImageUrl());
      return;
    }

    objectUrl = URL.createObjectURL(file);
    setImage(objectUrl);

    // New image starts centered; the user can immediately reposition it.
    focusX = 50;
    focusY = 50;
    updateUI();
  });

  window.addEventListener("beforeunload", () => {
    if (objectUrl) {
      URL.revokeObjectURL(objectUrl);
    }
  });

  setImage(getExistingImageUrl());
  updateUI();
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initPhotoCropper, { once: true });
} else {
  initPhotoCropper();
}
