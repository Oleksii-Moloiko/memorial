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

  const galleryLayoutClasses = [
    "layout-portrait-left",
    "layout-landscape-right",
    "layout-full",
    "layout-landscape-left",
    "layout-portrait-right",
  ];

  const galleryPattern = [
    "layout-portrait-left",
    "layout-landscape-right",
    "layout-landscape-right",
    "layout-landscape-right",
    "layout-full",
    "layout-landscape-left",
    "layout-landscape-left",
    "layout-landscape-left",
    "layout-portrait-right",
    "layout-full",
  ];

  const applyGalleryLayout = () => {
    let visibleIndex = 0;

    galleryCards.forEach((card) => {
      card.classList.remove(
        ...galleryLayoutClasses
      );

      if (card.classList.contains("is-hidden")) {
        return;
      }

      card.classList.add(
        galleryPattern[
          visibleIndex % galleryPattern.length
        ]
      );

      visibleIndex += 1;
    });
  };

  applyGalleryLayout();

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

      applyGalleryLayout();

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


const timelineCarousel = document.querySelector('[data-timeline-carousel]');

if (timelineCarousel) {
  const viewport = timelineCarousel.querySelector(
    '.timeline-carousel__viewport'
  );

  const track = timelineCarousel.querySelector(
    '[data-timeline-track]'
  );



  const ticksContainer = timelineCarousel.querySelector(
    '[data-timeline-ticks]'
  );

  const labelsContainer = timelineCarousel.querySelector(
    '[data-timeline-labels]'
  );

  const labels = labelsContainer
    ? Array.from(labelsContainer.children)
    : [];

  const cards = Array.from(
    timelineCarousel.querySelectorAll('[data-timeline-card]')
  );

  const MINOR_TICKS = 9;
  const majorTicks = [];
  let allTicks = [];

  const buildTimelineTicks = () => {
    if (!ticksContainer || !labels.length) return;

    ticksContainer.innerHTML = '';
    majorTicks.length = 0;

    labels.forEach((label, index) => {
      const major = document.createElement('i');

      major.className =
        'timeline-carousel__tick timeline-carousel__tick--major';

      ticksContainer.appendChild(major);
      majorTicks.push(major);

      if (index < labels.length - 1) {
        for (let i = 0; i < MINOR_TICKS; i += 1) {
          const minor = document.createElement('i');

          minor.className = 'timeline-carousel__tick';

          ticksContainer.appendChild(minor);
        }
      }
    });

    allTicks = Array.from(
      ticksContainer.querySelectorAll('.timeline-carousel__tick')
    );
  };

  const updateTimelineRuler = (scrollRatio, activeIndex) => {
    if (!allTicks.length || !labels.length) return;

    const safeRatio = Math.max(
      0,
      Math.min(scrollRatio, 1)
    );

    const safeIndex = Math.max(
      0,
      Math.min(activeIndex, labels.length - 1)
    );

    const filledIndex = Math.round(
      safeRatio * (allTicks.length - 1)
    );

    allTicks.forEach((tick, index) => {
      tick.classList.toggle(
        'is-filled',
        index <= filledIndex
      );
    });

    labels.forEach((label, index) => {
      label.classList.toggle(
        'is-current',
        index === safeIndex
      );
    });

    majorTicks.forEach((tick, index) => {
      tick.classList.toggle(
        'is-current',
        index === safeIndex
      );
    });
  };

  const mobileMedia = window.matchMedia('(max-width: 767px)');

  let currentX = 0;

  const getDesktopMaxScroll = () => {
    return Math.max(
      0,
      track.scrollWidth - viewport.clientWidth
    );
  };

  const updateDesktop = () => {
    if (mobileMedia.matches) return;

    const maxScroll = getDesktopMaxScroll();

    currentX = Math.max(
      0,
      Math.min(currentX, maxScroll)
    );

    track.style.transform =
      `translate3d(${-currentX}px, 0, 0)`;

    const scrollRatio =
      maxScroll > 0
        ? currentX / maxScroll
        : 0;

    let activeIndex = 0;

    if (cards.length > 1) {
      const cardStep =
        cards[1].offsetLeft - cards[0].offsetLeft;

      if (cardStep > 0) {
        activeIndex = Math.round(
          currentX / cardStep
        );
      }
    }

    activeIndex = Math.max(
      0,
      Math.min(activeIndex, cards.length - 1)
    );

    updateTimelineRuler(
      scrollRatio,
      activeIndex
    );
  };

  const updateMobile = () => {
    if (!mobileMedia.matches) return;

    const maxScroll =
      viewport.scrollWidth - viewport.clientWidth;

    const scrollRatio =
      maxScroll > 0
        ? viewport.scrollLeft / maxScroll
        : 0;

    let activeIndex = 0;

    if (cards.length > 1) {
      const cardStep =
        cards[1].offsetLeft - cards[0].offsetLeft;

      if (cardStep > 0) {
        activeIndex = Math.round(
          viewport.scrollLeft / cardStep
        );
      }
    }

    activeIndex = Math.max(
      0,
      Math.min(activeIndex, cards.length - 1)
    );

    updateTimelineRuler(
      scrollRatio,
      activeIndex
    );
  };

  const updateDesktopSectionHeight = () => {
    if (mobileMedia.matches) {
      timelineCarousel.style.height = '';
      return;
    }

    const maxScroll = getDesktopMaxScroll();

    const EXIT_HOLD = window.innerHeight * 0.35;

    const extraScroll =
      Math.max(
        window.innerHeight * 1.2,
        maxScroll
      ) + EXIT_HOLD;

    timelineCarousel.style.height =
      `${window.innerHeight + extraScroll}px`;
  };

  const updateDesktopFromScroll = () => {
    if (mobileMedia.matches) return;

    updateDesktopSectionHeight();

    const maxScroll = getDesktopMaxScroll();

    if (maxScroll <= 0) {
      currentX = 0;
      updateDesktop();
      return;
    }

    const rect = timelineCarousel.getBoundingClientRect();

    const scrollableDistance =
      timelineCarousel.offsetHeight - window.innerHeight;

    if (scrollableDistance <= 0) return;

    const scrolledInsideSection = -rect.top;

    const EXIT_HOLD = window.innerHeight * 0.35;

    const movementDistance = Math.max(
      1,
      scrollableDistance - EXIT_HOLD
    );

    const scrollProgress = Math.max(
      0,
      Math.min(
        scrolledInsideSection / movementDistance,
        1
      )
    );

    currentX = scrollProgress * maxScroll;

    updateDesktop();
  };

  const handleBreakpointChange = () => {
    if (mobileMedia.matches) {
      track.style.transform = 'none';
      viewport.scrollLeft = 0;
      updateMobile();
    } else {
      viewport.scrollLeft = 0;
      updateDesktopFromScroll();
    }
  };

  window.addEventListener(
    'scroll',
    updateDesktopFromScroll,
    { passive: true }
  );

  viewport.addEventListener(
    'scroll',
    updateMobile,
    { passive: true }
  );

  window.addEventListener('resize', () => {
    if (mobileMedia.matches) {
      timelineCarousel.style.height = '';
      updateMobile();
    } else {
      updateDesktopSectionHeight();
      updateDesktopFromScroll();
    }
  });

  mobileMedia.addEventListener(
    'change',
    handleBreakpointChange
  );

  buildTimelineTicks();
  handleBreakpointChange();
}
})();