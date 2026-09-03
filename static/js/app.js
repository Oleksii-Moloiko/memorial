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
 * Toast messages
 */

  const toasts =
    document.querySelectorAll("[data-toast]");

  toasts.forEach((toast, index) => {
    setTimeout(() => {
      toast.classList.add("show");
    }, index * 150);

    setTimeout(() => {
      toast.classList.remove("show");
    }, 5000 + index * 150);
  });

  const showToast = (message, type = "success") => {
    let toast =
      document.querySelector("[data-toast-ajax]");

    if (!toast) {
      toast = document.createElement("div");

      toast.className = "toast";
      toast.setAttribute("data-toast-ajax", "");
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");

      document.body.appendChild(toast);
    }

    toast.textContent = message;

    toast.classList.remove(
      "is-success",
      "is-error"
    );

    toast.classList.add(
      type === "error"
        ? "is-error"
        : "is-success"
    );

    toast.classList.add("show");

    clearTimeout(window.__toastTimer);

    window.__toastTimer = setTimeout(() => {
      toast.classList.remove("show");
    }, 5000);
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


  });

  /*
 * Life biography sidebar
 *
 * Високий sidebar рухається разом зі сторінкою.
 * При скролі вниз зупиняється, коли видно його низ.
 * При скролі вгору зупиняється під header.
 */

  const biographyAside =
    document.querySelector(".biography-aside");

  if (biographyAside) {
    const biographyDesktop =
      window.matchMedia("(min-width: 961px)");

    const STICKY_TOP = 118;
    const STICKY_BOTTOM = 24;

    let lastScrollY = window.scrollY;
    let stickyTop = STICKY_TOP;
    let ticking = false;

    const clamp = (value, min, max) =>
      Math.min(Math.max(value, min), max);

    const getStickyLimits = () => {
      const asideHeight =
        biographyAside.offsetHeight;

      const minTop = Math.min(
        STICKY_TOP,
        window.innerHeight -
          STICKY_BOTTOM -
          asideHeight
      );

      return {
        minTop,
        maxTop: STICKY_TOP,
      };
    };

    const resetBiographySticky = () => {
      lastScrollY = window.scrollY;

      if (!biographyDesktop.matches) {
        biographyAside.classList.remove(
          "is-sticky"
        );

        biographyAside.style.removeProperty(
          "--biography-sticky-top"
        );

        return;
      }

      const rect =
        biographyAside.getBoundingClientRect();

      const { minTop, maxTop } =
        getStickyLimits();

      stickyTop = clamp(
        rect.top,
        minTop,
        maxTop
      );

      biographyAside.style.setProperty(
        "--biography-sticky-top",
        `${stickyTop}px`
      );

      biographyAside.classList.add(
        "is-sticky"
      );
    };

    const updateBiographySticky = () => {
      ticking = false;

      if (!biographyDesktop.matches) {
        lastScrollY = window.scrollY;
        return;
      }

      const currentScrollY =
        window.scrollY;

      const scrollDelta =
        currentScrollY - lastScrollY;

      const { minTop, maxTop } =
        getStickyLimits();

      /*
       * Якщо sidebar повністю влазить у viewport,
       * використовуємо звичайний sticky під header.
       */
      if (
        biographyAside.offsetHeight <=
        window.innerHeight -
          STICKY_TOP -
          STICKY_BOTTOM
      ) {
        stickyTop = STICKY_TOP;
      } else {
      /*
       * Вниз:
       * stickyTop поступово зменшується,
       * доки низ sidebar не стане видимим.
       *
       * Вгору:
       * stickyTop збільшується,
       * доки верх не дійде до header.
       */
        stickyTop = clamp(
          stickyTop - scrollDelta,
          minTop,
          maxTop
        );
      }

      biographyAside.style.setProperty(
        "--biography-sticky-top",
        `${stickyTop}px`
      );

      lastScrollY = currentScrollY;
    };

    window.addEventListener(
      "scroll",
      () => {
        if (ticking) {
          return;
        }

        ticking = true;

        requestAnimationFrame(
          updateBiographySticky
        );
      },
      { passive: true }
    );

    window.addEventListener(
      "resize",
      resetBiographySticky
    );

    biographyDesktop.addEventListener(
      "change",
      resetBiographySticky
    );

    if ("ResizeObserver" in window) {
      const biographyResizeObserver =
        new ResizeObserver(() => {
          resetBiographySticky();
        });

      biographyResizeObserver.observe(
        biographyAside
      );
    }

    resetBiographySticky();
  }



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
  const galleryGrid =
    document.querySelector(".gallery-grid");

  const galleryEmpty =
    document.querySelector(
      "[data-gallery-empty]"
    );

  const galleryMoreButton =
    document.querySelector(
      "[data-gallery-more]"
    );

  const GALLERY_PAGE_SIZE = 10;

  let galleryVisibleLimit =
    GALLERY_PAGE_SIZE;

  let activeGalleryFilter = "all";

  const galleryUrlParams =
    new URLSearchParams(window.location.search);

  const requestedGalleryFilter =
    galleryUrlParams.get("category");

  const availableGalleryFilters =
    Array.from(filterButtons).map(
      (button) => button.dataset.filter
    );

  if (
    requestedGalleryFilter &&
    availableGalleryFilters.includes(
      requestedGalleryFilter
    )
  ) {
    activeGalleryFilter =
      requestedGalleryFilter;

    filterButtons.forEach((button) => {
      const isActive =
        button.dataset.filter ===
        requestedGalleryFilter;

      button.classList.toggle(
        "active",
        isActive
      );

      button.setAttribute(
        "aria-pressed",
        String(isActive)
      );
    });
  }

  const updateGalleryVisibility = () => {
    let matchedIndex = 0;

    galleryCards.forEach((card) => {
      const matchesFilter =
        activeGalleryFilter === "all" ||
        card.dataset.category === activeGalleryFilter;

      const shouldShow =
        matchesFilter &&
        matchedIndex < galleryVisibleLimit;

      card.classList.toggle(
        "is-hidden",
        !shouldShow
      );

      if (matchesFilter) {
        matchedIndex += 1;
      }
    });

    if (galleryMoreButton) {
      galleryMoreButton.hidden =
        matchedIndex <= galleryVisibleLimit;
    }

    applyGalleryLayout();
  };

  if (galleryMoreButton) {
    galleryMoreButton.addEventListener("click", () => {
      const scrollYBefore = window.scrollY;

      galleryVisibleLimit += GALLERY_PAGE_SIZE;

      updateGalleryVisibility();

      // Повертаємо користувача рівно в ту саму
      // позицію після перебудови галереї.
      requestAnimationFrame(() => {
        window.scrollTo({
          top: scrollYBefore,
          left: 0,
          behavior: "instant",
        });

        requestAnimationFrame(() => {
          window.scrollTo({
            top: scrollYBefore,
            left: 0,
            behavior: "instant",
          });

          if (!galleryMoreButton.hidden) {
            galleryMoreButton.focus({ preventScroll: true });
          }
        });
      });
    });
  }

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
  const galleryMobileMedia =
    window.matchMedia("(max-width: 700px)");

  const applyGalleryLayout = () => {
    if (!galleryGrid || !galleryCards.length) {
      return;
    }

    const allCards = Array.from(galleryCards).sort(
      (a, b) =>
        Number(a.dataset.galleryIndex) -
        Number(b.dataset.galleryIndex)
    );

  /*
   * Повертаємо картки з попередніх груп назад
   * перед повторною побудовою сітки.
   * Це важливо для роботи фільтрів.
   */
    allCards.forEach((card) => {
      galleryGrid.appendChild(card);
    });

    galleryGrid
      .querySelectorAll(".gallery-band")
      .forEach((band) => band.remove());

    allCards.forEach((card) => {
      card.classList.remove(...galleryLayoutClasses);
    });

    const visibleCards = allCards.filter(
      (card) => !card.classList.contains("is-hidden")
    );

    galleryGrid.classList.add("is-grouped");

/*
 * MOBILE
 * 1 vertical → 3 horizontal → repeat
 */
    if (galleryMobileMedia.matches) {
      let mobileIndex = 0;

      while (mobileIndex < visibleCards.length) {
        const group =
          visibleCards.slice(
          mobileIndex,
          mobileIndex + 4
        );

      const band =
        document.createElement("div");

      band.className =
        "gallery-band gallery-band--mobile";

      group.forEach((card, indexInGroup) => {
        if (indexInGroup === 0) {
          card.classList.add(
            "layout-portrait-left"
          );
        } else {
          card.classList.add(
            "layout-landscape-right"
          );
        }

        band.appendChild(card);
      });

      galleryGrid.appendChild(band);

      mobileIndex += group.length;
    }

    return;
  }

  let index = 0;
  let mirrored = false;

    while (index < visibleCards.length) {
      const splitCards = visibleCards.slice(
        index,
        index + 4
      );

      if (splitCards.length) {
        const band = document.createElement("div");

        band.className =
          "gallery-band gallery-band--split";

        const stack = document.createElement("div");


        stack.className =
          "gallery-band__stack";

        /*
 * Якщо для повного split-блоку не вистачає 4 фото,
 * показуємо залишок звичайними 16:9 на всю ширину.
 */
        if (splitCards.length < 4) {
          band.classList.remove("gallery-band--split");
          band.classList.add("gallery-band--partial");

          splitCards.forEach((card) => {
            card.classList.add("layout-full");
            band.appendChild(card);
          });

          galleryGrid.appendChild(band);

          index += splitCards.length;
          break;
        }

        if (!mirrored) {
        /*
         * 9:16 | 16:9
         *      | 16:9
         *      | 16:9
         */
          const portrait = splitCards[0];
          const landscapes = splitCards.slice(1);

          portrait.classList.add(
            "layout-portrait-left"
          );

          landscapes.forEach((card) => {
            card.classList.add(
              "layout-landscape-right"
            );

            stack.appendChild(card);
          });

          band.appendChild(portrait);
          band.appendChild(stack);
        } else {
        /*
         * 16:9 |
         * 16:9 | 9:16
         * 16:9 |
         */
          const hasFullSplit = splitCards.length === 4;

          const portrait = hasFullSplit
            ? splitCards[3]
            : null;

          const landscapes = hasFullSplit
            ? splitCards.slice(0, 3)
            : splitCards;

          if (!hasFullSplit) {
            band.classList.remove("gallery-band--split");
            band.classList.add("gallery-band--partial");
          }

          landscapes.forEach((card) => {
            card.classList.add(
              "layout-landscape-left"
            );

            stack.appendChild(card);
          });

          band.appendChild(stack);

          if (portrait) {
            portrait.classList.add(
              "layout-portrait-right"
            );

            band.appendChild(portrait);
          }
        }

        galleryGrid.appendChild(band);

        index += splitCards.length;
      }

    /*
     * Після кожних чотирьох фото —
     * велике 16:9.
     */
      if (index < visibleCards.length) {
        const fullCard = visibleCards[index];

        const fullBand =
          document.createElement("div");

        fullBand.className =
          "gallery-band gallery-band--full";

        fullCard.classList.add("layout-full");

        fullBand.appendChild(fullCard);
        galleryGrid.appendChild(fullBand);

        index += 1;
      }

      mirrored = !mirrored;
    }
  };

  galleryMobileMedia.addEventListener(
    "change",
    () => {
      applyGalleryLayout();
    }
  );

  const initialMatchingCount =
    Array.from(galleryCards).filter(
      (card) =>
        activeGalleryFilter === "all" ||
        card.dataset.category ===
          activeGalleryFilter
    ).length;

  if (galleryEmpty) {
    galleryEmpty.hidden =
      initialMatchingCount !== 0;
  }

  updateGalleryVisibility();

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const selectedCategory =
        button.dataset.filter;

      activeGalleryFilter =
        selectedCategory;

      galleryVisibleLimit =
        GALLERY_PAGE_SIZE;

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

      const matchingCount =
        Array.from(galleryCards).filter(
          (card) =>
            selectedCategory === "all" ||
            card.dataset.category ===
              selectedCategory
        ).length;

      if (galleryEmpty) {
        galleryEmpty.hidden =
          matchingCount !== 0;
      }

      updateGalleryVisibility();
    });
  });

  /*
   * Photo dialog
   */

  const galleryDialog =
    document.querySelector(".gallery-dialog");

  const dialogImage =
    galleryDialog?.querySelector("[data-dialog-image]");

  const dialogCaption =
    galleryDialog?.querySelector(".dialog-caption");

  const dialogPrev =
    galleryDialog?.querySelector(".dialog-nav.prev");

  const dialogNext =
    galleryDialog?.querySelector(".dialog-nav.next");

  const dialogCounter =
    galleryDialog?.querySelector(".dialog-counter");

  const dialogClose =
    galleryDialog?.querySelector(".dialog-close");

  let dialogPhotoList = [];
  let dialogPhotoIndex = 0;
  let dialogScrollY = 0;
  function lockDialogScroll() {
    dialogScrollY = window.scrollY;

    document.documentElement.classList.add("dialog-open");
    document.body.classList.add("dialog-open");

    document.body.style.top = `-${dialogScrollY}px`;
  }

  function unlockDialogScroll() {
    const html = document.documentElement;
    const body = document.body;

    /* Тимчасово вимикаємо smooth scroll,
       щоб повернення позиції не було видно */
    html.style.scrollBehavior = "auto";

    html.classList.remove("dialog-open");
    body.classList.remove("dialog-open");

    body.style.top = "";

    window.scrollTo({
      top: dialogScrollY,
      left: 0,
      behavior: "auto",
    });

    /* Повертаємо звичайний smooth scroll сайту */
    requestAnimationFrame(() => {
      html.style.scrollBehavior = "";
    });
  }


  function getVisibleGalleryPhotos() {
    return [
      ...document.querySelectorAll(".gallery-open"),
    ].filter((button) => button.offsetParent !== null);
  }

  function showDialogPhoto(index) {
    if (
      !dialogImage ||
      !dialogPhotoList.length ||
      index < 0 ||
      index >= dialogPhotoList.length
    ) {
      return;
    }

    const button = dialogPhotoList[index];

    dialogPhotoIndex = index;

    dialogImage.src = button.dataset.image || "";
    dialogImage.alt = button.dataset.alt || "";

    if (dialogCaption) {
      dialogCaption.textContent =
        button.dataset.caption || "";
    }

    if (dialogCounter) {
      dialogCounter.textContent =
        `${index + 1} / ${dialogPhotoList.length}`;
    }

    if (dialogPrev) {
      dialogPrev.disabled = index === 0;
    }

    if (dialogNext) {
      dialogNext.disabled =
        index === dialogPhotoList.length - 1;
    }
  }

  document.addEventListener("click", (event) => {
    const button =
      event.target.closest(".gallery-open");

    if (!button || !galleryDialog) {
      return;
    }

    dialogPhotoList =
      getVisibleGalleryPhotos();

    dialogPhotoIndex =
      dialogPhotoList.indexOf(button);

    if (dialogPhotoIndex === -1) {
      return;
    }

    showDialogPhoto(dialogPhotoIndex);

    if (!galleryDialog.open) {
      lockDialogScroll();
      galleryDialog.showModal();
    }

    requestAnimationFrame(() => {
      window.scrollTo({
        top: dialogScrollY,
        left: 0,
        behavior: "instant",
      });
    });
  });

  dialogPrev?.addEventListener("click", (event) => {
    event.stopPropagation();

    showDialogPhoto(
      dialogPhotoIndex - 1
    );
  });

  dialogNext?.addEventListener("click", (event) => {
    event.stopPropagation();

    showDialogPhoto(
      dialogPhotoIndex + 1
    );
  });

  dialogClose?.addEventListener("click", () => {
    galleryDialog?.close();
  });

  galleryDialog?.addEventListener(
    "keydown",
    (event) => {
      if (event.key === "ArrowLeft") {
        event.preventDefault();

        showDialogPhoto(
          dialogPhotoIndex - 1
        );
      }

      if (event.key === "ArrowRight") {
        event.preventDefault();

        showDialogPhoto(
          dialogPhotoIndex + 1
        );
      }

      if (event.key === "Escape") {
        galleryDialog.close();
      }
    }
  );

  galleryDialog?.addEventListener(
    "close",
    () => {
      unlockDialogScroll();

      if (dialogImage) {
        dialogImage.src = "";
        dialogImage.alt = "";
      }

      if (dialogCaption) {
        dialogCaption.textContent = "";
      }

      dialogPhotoList = [];
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

/*
 * Memories: submit without page reload
 */

const memorySubmitForm =
  document.getElementById("memory-submit-form");

if (memorySubmitForm) {
  memorySubmitForm.addEventListener(
    "submit",
    async (event) => {
      event.preventDefault();

      const submitButton =
        memorySubmitForm.querySelector(
          '[type="submit"]'
        );

      submitButton?.setAttribute(
        "disabled",
        "disabled"
      );

      memorySubmitForm
        .querySelectorAll(
          ".field-error, .form-errors"
        )
        .forEach((element) => element.remove());

      memorySubmitForm
        .querySelectorAll(
          '[aria-invalid="true"]'
        )
        .forEach((field) => {
          field.removeAttribute("aria-invalid");
        });

      try {
        const response = await fetch(
          memorySubmitForm.action,
          {
            method: "POST",
            body: new FormData(memorySubmitForm),
            headers: {
              "X-Requested-With": "XMLHttpRequest",
            },
          }
        );

        const data = await response.json();

        if (response.ok && data.success) {
          memorySubmitForm.reset();

          showToast(
            data.message ||
              "Дякуємо. Ваш спогад надіслано на модерацію."
          );

          return;
        }

        if (data.message) {
          showToast(
            data.message,
            "error"
          );

          return;
        }

        const errors = data.errors || {};

        if (Object.keys(errors).length) {
          showToast(
            "Будь ласка, перевірте форму та заповніть обов’язкові поля.",
           "error"
          );
        }

        Object.entries(errors).forEach(
          ([fieldName, fieldErrors]) => {
            const field =
              memorySubmitForm.elements[fieldName];

            if (!field) {
              return;
            }

            field.setAttribute(
              "aria-invalid",
              "true"
            );

            const errorElement =
              document.createElement("span");

            errorElement.className =
              "field-error";

            errorElement.setAttribute(
              "role",
              "alert"
            );

            errorElement.textContent =
              fieldErrors[0]?.message ||
              "Перевірте це поле.";

            const label =
              field.closest("label");

            if (label) {
              label.appendChild(errorElement);
            } else {
              field.insertAdjacentElement(
                "afterend",
                errorElement
              );
            }
          }
        );
      } catch (error) {
        showToast(
          "Не вдалося надіслати спогад. Спробуйте ще раз.",
          "error"
        );
      } finally {
        submitButton?.removeAttribute(
          "disabled"
        );
      }
    }
  );
}

/*
 * Memories: read more
 */

document.addEventListener("click", (event) => {
  const button = event.target.closest(".read-more");

  if (!button) {
    return;
  }

  const card = button.closest(".memory-card");

  if (!card) {
    return;
  }

  const isOpen = card.classList.toggle("is-open");

  button.setAttribute(
    "aria-expanded",
    String(isOpen)
  );

  button.textContent =
    isOpen
      ? "Згорнути"
      : "Дивитись більше";

  if (!isOpen) {
    card.scrollIntoView({
      block: "nearest",
      behavior: "smooth",
    });
  }
});

let dialogTouchStartX = null;
let dialogTouchStartY = null;

galleryDialog?.addEventListener(
  "touchstart",
  (event) => {
    const touch = event.touches[0];

    dialogTouchStartX = touch.clientX;
    dialogTouchStartY = touch.clientY;
  },
  { passive: true }
);

galleryDialog?.addEventListener(
  "touchend",
  (event) => {
    if (
      dialogTouchStartX === null ||
      dialogTouchStartY === null
    ) {
      return;
    }

    const touch = event.changedTouches[0];

    const deltaX =
      touch.clientX - dialogTouchStartX;

    const deltaY =
      touch.clientY - dialogTouchStartY;

    dialogTouchStartX = null;
    dialogTouchStartY = null;

    // Ігноруємо вертикальний жест.
    if (
      Math.abs(deltaY) >
      Math.abs(deltaX)
    ) {
      return;
    }

    // Короткий рух не вважаємо свайпом.
    if (Math.abs(deltaX) < 50) {
      return;
    }

    if (deltaX < 0) {
      showDialogPhoto(
        dialogPhotoIndex + 1
      );
    } else {
      showDialogPhoto(
        dialogPhotoIndex - 1
      );
    }
  },
  { passive: true }
);

})();
