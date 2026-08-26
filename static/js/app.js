(() => {
  const qs = new URLSearchParams(location.search);
  const mode =
    qs.get("view") === "wireframe"
      ? "wireframe"
      : "design";

  document.body.classList.toggle(
    "wireframe",
    mode === "wireframe"
  );

  document
    .querySelector(`.mode-${mode}`)
    ?.classList.add("active");

  const navigationBase =
    location.protocol === "about:"
      ? "https://prototype.local/"
      : location.href;

  document
    .querySelectorAll("[data-preserve-query]")
    .forEach((link) => {
      const href = link.getAttribute("href");

      if (
        !href ||
        href.startsWith("#") ||
        href.startsWith("http")
      ) {
        return;
      }

      const url = new URL(href, navigationBase);

      url.searchParams.set("view", mode);

      link.setAttribute(
        "href",
        url.pathname.split("/").pop() + url.search
      );
    });

  /*
   * Mobile navigation
   */

  const navToggle =
    document.querySelector(".nav-toggle");

  const nav =
    document.querySelector(".primary-nav");

  navToggle?.addEventListener("click", () => {
    if (!nav) {
      return;
    }

    const open = nav.classList.toggle("open");

    navToggle.setAttribute(
      "aria-expanded",
      String(open)
    );
  });

  /*
   * Grid overlay
   */

  const gridToggle =
    document.querySelector(".grid-toggle");

  gridToggle?.addEventListener("click", () => {
    const active =
      document.body.classList.toggle("grid-overlay");

    gridToggle.setAttribute(
      "aria-pressed",
      String(active)
    );
  });

  /*
   * Current year
   */

  document
    .querySelectorAll("[data-year]")
    .forEach((element) => {
      element.textContent =
        new Date().getFullYear();
    });

  /*
   * Demo toast
   */

  const toast =
    document.querySelector(".toast");

  const showToast = (message) => {
    if (!toast) {
      return;
    }

    toast.textContent = message;
    toast.classList.add("show");

    clearTimeout(window.__toastTimer);

    window.__toastTimer = setTimeout(() => {
      toast.classList.remove("show");
    }, 2400);
  };

  document
    .querySelectorAll(".demo-action")
    .forEach((element) => {
      element.addEventListener("click", (event) => {
        event.preventDefault();

        showToast(
          "Демонстраційна дія: додайте перевірене посилання або файл."
        );
      });
    });

  /*
   * Legacy demo form
   *
   * Працює лише для елементів із класом .demo-form.
   * Реальна форма спогадів не повинна мати цей клас.
   */

  const demoForm =
    document.querySelector(".demo-form");

  demoForm?.addEventListener("submit", (event) => {
    event.preventDefault();

    showToast(
      "Демо: повідомлення передано б на ручну модерацію."
    );

    demoForm.reset();

    const counter =
      demoForm.querySelector(".counter");

    if (counter) {
      counter.textContent = "0 / 500";
    }
  });

  /*
   * Generic textarea counter
   */

  document
    .querySelectorAll("textarea[maxlength]")
    .forEach((textarea) => {
      const counter =
        textarea.parentElement?.querySelector(
          ".counter"
        );

      if (!counter) {
        return;
      }

      const updateCounter = () => {
        counter.textContent =
          `${textarea.value.length} / ${textarea.maxLength}`;
      };

      textarea.addEventListener(
        "input",
        updateCounter
      );

      updateCounter();
    });

  /*
   * Photo gallery filters
   */

  const filterButtons =
    document.querySelectorAll(
      ".filter-chip[data-filter]"
    );

  const galleryCards =
    document.querySelectorAll(
      ".gallery-card[data-category]"
    );

  const galleryEmpty =
    document.querySelector(
      "[data-gallery-empty]"
    );

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const selectedCategory =
        button.dataset.filter;

      let visibleCount = 0;

      filterButtons.forEach((item) => {
        const isActive = item === button;

        item.classList.toggle(
          "active",
          isActive
        );

        item.setAttribute(
          "aria-pressed",
          String(isActive)
        );
      });

      galleryCards.forEach((card) => {
        const shouldShow =
          selectedCategory === "all" ||
          card.dataset.category ===
            selectedCategory;

        card.classList.toggle(
          "is-hidden",
          !shouldShow
        );

        if (shouldShow) {
          visibleCount += 1;
        }
      });

      if (galleryEmpty) {
        galleryEmpty.hidden =
          visibleCount !== 0;
      }
    });
  });

  /*
   * Photo dialog
   */

  const galleryDialog =
    document.querySelector(
      ".gallery-dialog"
    );

  const dialogImage =
    galleryDialog?.querySelector(
      "[data-dialog-image]"
    );

  const dialogCaption =
    galleryDialog?.querySelector(
      ".dialog-caption"
    );

  document
    .querySelectorAll(".gallery-open")
    .forEach((button) => {
      button.addEventListener("click", () => {
        if (
          !galleryDialog ||
          !dialogImage ||
          !dialogCaption
        ) {
          return;
        }

        dialogImage.src =
          button.dataset.image || "";

        dialogImage.alt =
          button.dataset.alt || "";

        dialogCaption.textContent =
          button.dataset.caption || "";

        galleryDialog.showModal();
      });
    });

  galleryDialog
    ?.querySelector(".dialog-close")
    ?.addEventListener("click", () => {
      galleryDialog.close();
    });

  galleryDialog?.addEventListener(
    "click",
    (event) => {
      if (event.target === galleryDialog) {
        galleryDialog.close();
      }
    }
  );

  galleryDialog?.addEventListener(
    "close",
    () => {
      if (dialogImage) {
        dialogImage.src = "";
        dialogImage.alt = "";
      }

      if (dialogCaption) {
        dialogCaption.textContent = "";
      }
    }
  );
/*
 * Hero scroll hint
 */

const heroScrollDot =
  document.querySelector(".hero-scroll__dot");

heroScrollDot?.addEventListener("click", () => {
  const hero =
    document.querySelector(".hero");

  const nextSection =
    hero?.nextElementSibling;

  nextSection?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
});

})();