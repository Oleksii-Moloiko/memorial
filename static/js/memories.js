(() => {
  if (document.body.dataset.page !== "memories") {
    return;
  }

  const mobile = window.matchMedia("(max-width: 760px)");
  let previews = [];

  const renderPreviews = () => {
    previews.forEach(({ card, box, teaser }) => {
      box.textContent = mobile.matches
        ? card.dataset.memoryFull
        : teaser;
    });
  };

  const collectPreviews = () => {
    previews = Array.from(
      document.querySelectorAll(".memories-grid .memory-card")
    ).map((card) => ({
      card,
      box: card.querySelector(".memory-text"),
      teaser: card.querySelector(".memory-text").textContent,
    }));

    renderPreviews();
  };

  mobile.addEventListener("change", renderPreviews);
  window.addEventListener("memory-results-updated", collectPreviews);
  collectPreviews();

  const labels = document.querySelector("[data-memory-labels]").dataset;

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
      aria-label=""
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
          aria-label=""
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

        </span>
      </div>

    </div>
  `;

  dialog.querySelector(".memory-dialog__backdrop").setAttribute("aria-label", labels.close);
  dialog.querySelector(".memory-dialog__close").setAttribute("aria-label", labels.closeMemory);
  dialog.querySelector(".memory-dialog__foot span:last-child").textContent = labels.esc;
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
      `${full.trim().length.toLocaleString(document.documentElement.lang)} ${labels.characters}`;

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

  window.addEventListener(
    "memory-results-updated",
    scheduleCarouselUpdate
  );

  scheduleCarouselUpdate();
})();
// Оновлюємо спогади без перезавантаження сторінки.
(() => {
  const grid = document.querySelector(
    'body[data-page="memories"] .memories-grid'
  );
  const container = grid?.parentElement;
  const bar = container?.querySelector(".filter-bar");

  if (!grid || !container || !bar) return;

  let currentRequest = null;

  const loadResults = async (url, pushHistory = true) => {
    currentRequest?.abort();

    const request = new AbortController();
    currentRequest = request;
    grid.setAttribute("aria-busy", "true");

    try {
      const response = await fetch(url, {
        signal: request.signal,
        headers: { Accept: "text/html" },
      });

      if (!response.ok) {
        throw new Error("Не вдалося завантажити спогади");
      }

      const html = await response.text();

      if (request !== currentRequest || request.signal.aborted) return;

      const page = new DOMParser().parseFromString(html, "text/html");
      const nextGrid = page.querySelector(
        'body[data-page="memories"] .memories-grid'
      );
      const nextBar = nextGrid?.parentElement.querySelector(".filter-bar");
      const nextPagination = nextGrid?.parentElement.querySelector(
        ".memories-pagination"
      );

      if (!nextGrid || !nextBar) {
        throw new Error("Неочікувана відповідь сервера");
      }

      const links = Array.from(
        bar.querySelectorAll("a[data-memory-filter]")
      );
      const nextLinks = new Map(
        Array.from(
          nextBar.querySelectorAll("a[data-memory-filter]")
        ).map((link) => [link.dataset.memoryFilter, link])
      );

      if (
        links.length !== nextLinks.size ||
        links.some((link) => !nextLinks.has(link.dataset.memoryFilter))
      ) {
        throw new Error("Список категорій змінився");
      }

      const pagination = container.querySelector(".memories-pagination");
      const focusWasInPagination =
        pagination?.contains(document.activeElement);
      const barTop = bar.getBoundingClientRect().top;
      const barLeft = bar.scrollLeft;

      if (pushHistory && url.href !== window.location.href) {
        history.pushState(null, "", url.href);
      }

      // Зберігаємо самі кнопки, тому їхній фокус не втрачається.
      links.forEach((link) => {
        const nextLink = nextLinks.get(link.dataset.memoryFilter);

        link.setAttribute("href", nextLink.getAttribute("href"));
        link.setAttribute(
          "aria-pressed",
          nextLink.getAttribute("aria-pressed")
        );

        const count = link.querySelector(".filter-chip__n");
        const nextCount = nextLink.querySelector(".filter-chip__n");

        if (count && nextCount) {
          count.textContent = nextCount.textContent;
        }
      });

      grid.replaceChildren(
        ...Array.from(nextGrid.childNodes).map((node) =>
          document.importNode(node, true)
        )
      );

      if (nextPagination) {
        const replacement = document.importNode(nextPagination, true);

        if (pagination) {
          pagination.replaceWith(replacement);
        } else {
          grid.after(replacement);
        }
      } else {
        pagination?.remove();
      }

      grid.scrollTo({ left: 0, behavior: "instant" });

      window.dispatchEvent(new Event("memory-results-updated"));

      if (focusWasInPagination) {
        grid.setAttribute("tabindex", "-1");
        grid.focus({ preventScroll: true });
      }

      bar.scrollTo({ left: barLeft, behavior: "instant" });

      window.scrollTo({
        top: window.scrollY + bar.getBoundingClientRect().top - barTop,
        behavior: "instant",
      });
    } catch (error) {
      if (request.signal.aborted || request !== currentRequest) return;

      // Якщо фоновий запит не спрацював, відкриваємо звичайну сторінку.
      window.location.assign(url.href);
    } finally {
      if (request === currentRequest) {
        grid.removeAttribute("aria-busy");
        currentRequest = null;
      }
    }
  };

  container.addEventListener("click", (event) => {
    const link = event.target.closest(
      "a[data-memory-filter], .memories-pagination a"
    );

    if (
      !link ||
      !container.contains(link) ||
      event.defaultPrevented ||
      event.button !== 0 ||
      event.ctrlKey ||
      event.metaKey ||
      event.shiftKey ||
      event.altKey ||
      link.hasAttribute("download") ||
      (link.target && link.target !== "_self")
    ) {
      return;
    }

    const url = new URL(link.href, window.location.href);

    if (
      url.origin !== window.location.origin ||
      url.pathname !== window.location.pathname
    ) {
      return;
    }

    event.preventDefault();
    loadResults(url);
  });

  window.addEventListener("popstate", () => {
    loadResults(new URL(window.location.href), false);
  });
})();