(() => {
  const cards = Array.from(
    document.querySelectorAll(
      'body[data-page="memories"] .memory-card'
    )
  );

  if (!cards.length) {
    return;
  }

  const mobile = window.matchMedia("(max-width: 760px)");
  const previews = cards.map((card) => ({
    card,
    box: card.querySelector(".memory-text"),
    teaser: card.querySelector(".memory-text").textContent,
  }));
  const renderPreviews = () => previews.forEach(({ card, box, teaser }) => {
    box.textContent = mobile.matches ? card.dataset.memoryFull : teaser;
  });
  mobile.addEventListener("change", renderPreviews);
  renderPreviews();

  const lang =
    document.documentElement.lang || "uk";

  const isEnglish =
    lang.toLowerCase().startsWith("en");

  const labels = {
    close: isEnglish ? "Close" : "Закрити",
    closeMemory: isEnglish
      ? "Close memory"
      : "Закрити спогад",
    characters: isEnglish
      ? "characters"
      : "символів",
    esc: isEnglish
      ? "Esc — close"
      : "Esc — закрити",
  };

  const dialog =
    document.createElement("div");

  dialog.className = "memory-dialog";

  dialog.setAttribute(
    "role",
    "dialog"
  );

  dialog.setAttribute(
    "aria-modal",
    "true"
  );

  dialog.setAttribute(
    "aria-labelledby",
    "memory-dialog-author"
  );

  dialog.setAttribute(
    "aria-hidden",
    "true"
  );

  dialog.innerHTML = `
    <button
      class="memory-dialog__backdrop"
      type="button"
      tabindex="-1"
      aria-label="${labels.close}"
    ></button>

    <div class="memory-dialog__panel">

      <div class="memory-dialog__head">

        <div class="memory-dialog__who">
          <p
            class="memory-dialog__author"
            id="memory-dialog-author"
          ></p>

          <p
            class="memory-dialog__rel"
          ></p>
        </div>

        <button
          class="memory-dialog__close"
          type="button"
          aria-label="${labels.closeMemory}"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            aria-hidden="true"
          >
            <path
              d="M6 6l12 12M18 6L6 18"
            ></path>
          </svg>
        </button>

      </div>

      <div
        class="memory-dialog__body"
        tabindex="-1"
      >
        <div
          class="memory-dialog__text"
        ></div>

        <div
          class="memory-dialog__progress"
          aria-hidden="true"
        >
          <i></i>
        </div>
      </div>

      <div class="memory-dialog__foot">
        <span
          class="memory-dialog__len"
        ></span>

        <span>
          ${labels.esc}
        </span>
      </div>

    </div>
  `;

  document.body.appendChild(dialog);

  const dialogBody =
    dialog.querySelector(
      ".memory-dialog__body"
    );

  const textBox =
    dialog.querySelector(
      ".memory-dialog__text"
    );

  const authorBox =
    dialog.querySelector(
      ".memory-dialog__author"
    );

  const relationBox =
    dialog.querySelector(
      ".memory-dialog__rel"
    );

  const lengthBox =
    dialog.querySelector(
      ".memory-dialog__len"
    );

  const progressBar =
    dialog.querySelector(
      ".memory-dialog__progress i"
    );

  const closeButton =
    dialog.querySelector(
      ".memory-dialog__close"
    );

  const backdrop =
    dialog.querySelector(
      ".memory-dialog__backdrop"
    );

  let lastFocus = null;

  const openDialog = (card) => {
    const full =
      card.dataset.memoryFull || "";

    const author =
      card.querySelector(
        ".memory-author"
      );

    const relation =
      card.querySelector(
        ".memory-relation"
      );

    textBox.innerHTML = "";

    full
      .split(/\n{2,}/)
      .forEach((part) => {
        const text = part.trim();

        if (!text) {
          return;
        }

        const paragraph =
          document.createElement("p");

        paragraph.textContent = text;

        textBox.appendChild(
          paragraph
        );
      });

    authorBox.textContent =
      author?.textContent.trim() || "";

    relationBox.textContent =
      relation?.textContent.trim() || "";

    relationBox.hidden =
      !relationBox.textContent;

    lengthBox.textContent =
      `${full.trim().length.toLocaleString(lang)} ${labels.characters}`;

    lastFocus =
      document.activeElement;

    dialog.classList.add(
      "is-open"
    );

    dialog.setAttribute(
      "aria-hidden",
      "false"
    );

    document.body.classList.add(
      "has-modal"
    );

    dialogBody.scrollTop = 0;

    progressBar.style.width =
      "0%";

    dialogBody.focus();
  };

  const closeDialog = () => {
    dialog.classList.remove(
      "is-open"
    );

    dialog.setAttribute(
      "aria-hidden",
      "true"
    );

    document.body.classList.remove(
      "has-modal"
    );

    if (
      lastFocus &&
      typeof lastFocus.focus ===
        "function"
    ) {
      lastFocus.focus();
    }
  };

  document.addEventListener(
    "click",
    (event) => {
      const button =
        event.target.closest(
          "[data-memory-open]"
        );

      if (!button) {
        return;
      }

      const card =
        button.closest(
          ".memory-card"
        );

      if (!card) {
        return;
      }

      openDialog(card);
    }
  );

  closeButton.addEventListener(
    "click",
    closeDialog
  );

  backdrop.addEventListener(
    "click",
    closeDialog
  );

  document.addEventListener(
    "keydown",
    (event) => {
      if (
        !dialog.classList.contains(
          "is-open"
        )
      ) {
        return;
      }

      if (event.key === "Escape") {
        event.preventDefault();
        closeDialog();
        return;
      }

      if (event.key !== "Tab") {
        return;
      }

      const focusable = [
        closeButton,
        dialogBody,
      ];

      const current =
        focusable.indexOf(
          document.activeElement
        );

      let next = event.shiftKey
        ? current - 1
        : current + 1;

      if (current === -1) {
        next = 0;
      }

      if (next < 0) {
        next =
          focusable.length - 1;
      }

      if (
        next >= focusable.length
      ) {
        next = 0;
      }

      event.preventDefault();

      focusable[next].focus();
    }
  );

  dialogBody.addEventListener(
    "scroll",
    () => {
      const max =
        dialogBody.scrollHeight -
        dialogBody.clientHeight;

      const progress =
        max > 0
          ? (
              dialogBody.scrollTop /
              max
            ) * 100
          : 0;

      progressBar.style.width =
        `${progress}%`;
    },
    { passive: true }
  );
    /*
   * Mobile memories carousel progress
   */

  const grid = document.querySelector(
    'body[data-page="memories"] .memories-grid'
  );

  const carouselProgress =
    document.querySelector(
      ".memories-progress"
    );

  const carouselFill =
    carouselProgress?.querySelector(
      ".memories-progress__fill"
    );

  const carouselCount =
    carouselProgress?.querySelector(
      ".memories-progress__count"
    );

  const mobileQuery =
    window.matchMedia(
      "(max-width: 760px)"
    );

  const updateCarouselProgress = () => {
    if (
      !grid ||
      !carouselProgress ||
      !carouselFill ||
      !carouselCount
    ) {
      return;
    }

    const visibleCards =
      Array.from(
        grid.querySelectorAll(
          ".memory-card"
        )
      ).filter(
        (card) => !card.hidden
      );

    const total =
      visibleCards.length;

    if (
      !mobileQuery.matches ||
      total < 2
    ) {
      carouselProgress.hidden = true;
      return;
    }

    carouselProgress.hidden = false;

    const firstCard =
      visibleCards[0];

    const cardWidth =
      firstCard.getBoundingClientRect()
        .width;

    const styles =
      getComputedStyle(grid);

    const gap =
      parseFloat(styles.columnGap) ||
      parseFloat(styles.gap) ||
      14;

    const step =
      cardWidth + gap;

    let index =
      Math.round(
        grid.scrollLeft / step
      );

    index = Math.max(
      0,
      Math.min(
        index,
        total - 1
      )
    );

    carouselCount.textContent =
      `${index + 1} / ${total}`;

    carouselFill.style.width =
      `${100 / total}%`;

    carouselFill.style.transform =
      `translateX(${index * 100}%)`;
  };

  let carouselFrame = null;

  const scheduleCarouselUpdate =
    () => {
      if (
        carouselFrame !== null
      ) {
        return;
      }

      carouselFrame =
        requestAnimationFrame(
          () => {
            carouselFrame = null;
            updateCarouselProgress();
          }
        );
    };

  grid?.addEventListener(
    "scroll",
    scheduleCarouselUpdate,
    { passive: true }
  );

  window.addEventListener(
    "resize",
    scheduleCarouselUpdate
  );

  mobileQuery.addEventListener(
    "change",
    scheduleCarouselUpdate
  );

  document.addEventListener(
    "click",
    (event) => {
      if (
        event.target.closest(
          "[data-memory-filter]"
        )
      ) {
        requestAnimationFrame(
          scheduleCarouselUpdate
        );
      }
    }
  );

  scheduleCarouselUpdate();
})();