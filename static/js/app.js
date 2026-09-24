(() => {
  /*
 * Mobile navigation
 */

  const navToggle =
    document.querySelector(".nav-toggle");

  const nav =
    document.querySelector(".primary-nav");

  const prefersReducedMotion =
    window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    );

  function openMobileNav() {
    if (!nav || !navToggle) {
      return;
    }

    nav.classList.remove("is-closing");
    nav.classList.add("open");

    navToggle.setAttribute(
      "aria-expanded",
      "true"
    );
  }

  function closeMobileNav({
    returnFocus = false,
    } = {}) {
    if (!nav || !navToggle) {
      return;
    }

    if (!nav.classList.contains("open")) {
      return;
    }

    navToggle.setAttribute(
      "aria-expanded",
      "false"
    );

    /*
     * При reduced motion не чекаємо transitionend,
     * бо анімація вимкнена.
     */
    if (prefersReducedMotion.matches) {
      nav.classList.remove(
        "open",
        "is-closing"
      );

      if (returnFocus) {
        navToggle.focus();
      }

      return;
    }

    nav.classList.add("is-closing");
    nav.classList.remove("open");

    const finishClosing = (event) => {
      if (
        event.target !== nav ||
        event.propertyName !== "opacity"
      ) {
        return;
      }

      nav.classList.remove("is-closing");

      nav.removeEventListener(
        "transitionend",
        finishClosing
      );

      if (returnFocus) {
        navToggle.focus();
      }
    };

    nav.addEventListener(
      "transitionend",
      finishClosing
    );
  }

  navToggle?.addEventListener("click", () => {
    if (!nav) {
      return;
    }

    if (nav.classList.contains("open")) {
      closeMobileNav();
    } else {
      openMobileNav();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      nav?.classList.contains("open")
    ) {
      event.preventDefault();

      closeMobileNav({
        returnFocus: true,
      });
    }
  });

  nav?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      closeMobileNav();
    });
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

  const dialogImageContainer =
    galleryDialog?.querySelector(".dialog-image");

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
  function updatePhotoDialogNavPosition() {
    if (
      !dialogImage ||
      !dialogImageContainer
    ) {
      return;
    }

    const imageRect =
      dialogImage.getBoundingClientRect();

    const containerRect =
      dialogImageContainer.getBoundingClientRect();

    const leftInset =
      imageRect.left - containerRect.left;

    const rightInset =
      containerRect.right - imageRect.right;

    dialogImageContainer.style.setProperty(
      "--photo-left-inset",
      `${leftInset}px`
    );

    dialogImageContainer.style.setProperty(
      "--photo-right-inset",
      `${rightInset}px`
    );
  }
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
      galleryDialog.focus({ preventScroll: true });
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

  document.addEventListener("keydown", (event) => {
    if (!galleryDialog?.open) {
      return;
    }

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
  });

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
    const memoryTextField =
      memorySubmitForm.elements.text;

    const memoryLimitHint =
      memorySubmitForm.querySelector(
        "[data-memory-limit-hint]"
      );

    const updateMemoryLimitHint = () => {
      if (!memoryTextField || !memoryLimitHint) {
        return;
      }

      const maxLength =
        Number(memoryTextField.maxLength);

      memoryLimitHint.hidden =
        !maxLength ||
        memoryTextField.value.length < maxLength;
    };

    memoryTextField?.addEventListener(
      "input",
      updateMemoryLimitHint
    );

    memorySubmitForm.addEventListener(
      "reset",
      () => {
        window.requestAnimationFrame(
          updateMemoryLimitHint
        );
      }
    );

    updateMemoryLimitHint();

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
            data.message || memorySubmitForm.dataset.successMessage
          );

          return;
        }

        showToast(
          data.message || memorySubmitForm.dataset.errorMessage,
          "error"
        );

        const errors = data.errors || {};

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
              memorySubmitForm.dataset.invalidMessage;

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
          memorySubmitForm.dataset.errorMessage,
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
      ? (button.dataset.lessLabel || "Згорнути")
      : (button.dataset.moreLabel || "Дивитись більше");

  if (!isOpen) {
    card.scrollIntoView({
      block: card.classList.contains("quote-memory-card") ? "start" : "nearest",
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "auto" : "smooth",
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

  /*
   * Language switcher
   */

  document
    .querySelectorAll("[data-language-switcher]")
    .forEach((switcher) => {
      const trigger =
        switcher.querySelector("[data-language-trigger]");

      const menu =
        switcher.querySelector("[data-language-menu]");

      if (!trigger || !menu) {
        return;
      }

      const close = () => {
        menu.hidden = true;

        trigger.setAttribute(
          "aria-expanded",
          "false"
        );
      };

      const open = () => {
        menu.hidden = false;

        trigger.setAttribute(
          "aria-expanded",
          "true"
        );
      };

      trigger.addEventListener("click", () => {
        if (menu.hidden) {
          open();
        } else {
          close();
        }
      });

      document.addEventListener("click", (event) => {
        if (!switcher.contains(event.target)) {
          close();
        }
      });

      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !menu.hidden) {
          close();
          trigger.focus();
        }
      });
    });

})();

/*
 * Memories: category filters
 */

(() => {
  const grid = document.querySelector(
    'body[data-page="memories"] .memories-grid'
  );

  const filters = Array.from(
    document.querySelectorAll("button[data-memory-filter]")
  );

  if (!grid || !filters.length) {
    return;
  }

  const cards = Array.from(
    grid.querySelectorAll(".memory-card")
  );

  const readCategories = () => {
    const selected = (new URLSearchParams(location.search).get("category") || "").split(",");
    return filters.map((filter) => filter.dataset.memoryFilter)
      .filter((category) => selected.includes(category));
  };
  let activeCategories = readCategories();

  const applyFilters = (updateUrl = false) => {
    cards.forEach((card) => {
      const category =
        card.dataset.memoryCategory || "";

      const visible =
        activeCategories.length === 0 ||
        activeCategories.includes(category);

      card.hidden = !visible;
    });

    filters.forEach((filter) => {
      const active = activeCategories.includes(
        filter.dataset.memoryFilter
      );

      filter.setAttribute(
        "aria-pressed",
        String(active)
      );
    });

    if (updateUrl) {
      const url = new URL(location.href);
      if (activeCategories.length) url.searchParams.set("category", activeCategories.join(","));
      else url.searchParams.delete("category");
      history.pushState(null, "", url);
    }

    // Після зміни категорій на мобільному
    // повертаємо карусель на початок.
    grid.scrollLeft = 0;

    window.dispatchEvent(
      new CustomEvent("memory-filter-change")
    );
  };

  filters.forEach((filter) => {
    filter.addEventListener("click", () => {
      const category =
        filter.dataset.memoryFilter;

      if (
        activeCategories.includes(category)
      ) {
        activeCategories =
          activeCategories.filter(
            (item) => item !== category
          );
      } else {
        activeCategories.push(category);
      }

      applyFilters(true);
    });
  });

  window.addEventListener("popstate", () => {
    activeCategories = readCategories();
    applyFilters();
  });
  applyFilters();
})();


(() => {
  const grid = document.querySelector(
    'body[data-page="memories"] .memories-grid'
  );

  if (!grid) return;

  const progress = grid.nextElementSibling;

  if (
    !progress?.classList.contains(
      "memories-progress"
    )
  ) {
    return;
  }

  const fill = progress.querySelector(
    ".memories-progress__fill"
  );

  const count = progress.querySelector(
    ".memories-progress__count"
  );

  const cards = Array.from(
    grid.querySelectorAll(".memory-card")
  );

  if (!fill || !count) return;

  const mobile = window.matchMedia(
    "(max-width: 760px)"
  );

  let frame = null;

  const update = () => {
    frame = null;

    const visibleCards = cards.filter(
      (card) => !card.hidden
    );

    const total = visibleCards.length;

    // На десктопі або якщо залишилась
    // одна картка — progress не потрібний.
    progress.hidden =
      !mobile.matches || total < 2;

    if (progress.hidden) {
      return;
    }

    const cardWidth =
      visibleCards[0].getBoundingClientRect().width;

    const gap = 14;

    const step = cardWidth + gap;

    let index = Math.round(
      grid.scrollLeft / step
    );

    if (index < 0) {
      index = 0;
    }

    if (index > total - 1) {
      index = total - 1;
    }

    count.textContent =
      `${index + 1} / ${total}`;

    fill.style.width =
      `${100 / total}%`;

    fill.style.transform =
      `translateX(${index * 100}%)`;
  };

  const scheduleUpdate = () => {
    if (frame !== null) {
      return;
    }

    frame =
      window.requestAnimationFrame(update);
  };

  grid.addEventListener(
    "scroll",
    scheduleUpdate,
    { passive: true }
  );

  window.addEventListener(
    "resize",
    scheduleUpdate
  );

  mobile.addEventListener(
    "change",
    scheduleUpdate
  );

  // Наші category filters кидають цю подію.
  window.addEventListener(
    "memory-filter-change",
    scheduleUpdate
  );

  if ("ResizeObserver" in window) {
    const observer =
      new ResizeObserver(scheduleUpdate);

    observer.observe(grid);
  }

  document.fonts?.ready.then(
    scheduleUpdate
  );

  scheduleUpdate();
})();

(() => {
  /*
   * Video dialog
   */

  const videoDialog =
    document.querySelector(".video-dialog");

  const videoDialogPlayer =
    videoDialog?.querySelector(".video-dialog-player");

  const videoDialogTitle =
    videoDialog?.querySelector(".video-dialog-title");

  const videoDialogClose =
    videoDialog?.querySelector(".video-dialog-close");

  const videoDialogPrev =
    videoDialog?.querySelector(".video-dialog-nav.prev");

  const videoDialogNext =
    videoDialog?.querySelector(".video-dialog-nav.next");

  const videoDialogCounter =
    videoDialog?.querySelector(".video-dialog-counter");

  let videoDialogList = [];
  let videoDialogIndex = 0;
  let videoDialogScrollY = 0;


  function lockVideoDialogScroll() {
    videoDialogScrollY = window.scrollY;

    document.documentElement.classList.add(
      "dialog-open"
    );

    document.body.classList.add(
      "dialog-open"
    );

    document.body.style.top =
      `-${videoDialogScrollY}px`;
  }


  function unlockVideoDialogScroll() {
    const html = document.documentElement;
    const body = document.body;

    html.style.scrollBehavior = "auto";

    html.classList.remove("dialog-open");
    body.classList.remove("dialog-open");

    body.style.top = "";

    window.scrollTo({
      top: videoDialogScrollY,
      left: 0,
      behavior: "auto",
    });

    requestAnimationFrame(() => {
      html.style.scrollBehavior = "";
    });
  }


  function getVideoDialogItems() {
    return [
      ...document.querySelectorAll(".video-open"),
    ];
  }


  function showDialogVideo(index) {
    if (
      !videoDialogPlayer ||
      !videoDialogList.length ||
      index < 0 ||
      index >= videoDialogList.length
    ) {
      return;
    }

    const button = videoDialogList[index];

    videoDialogIndex = index;

  /*
   * Зупиняємо попереднє відео перед
   * перемиканням на нове.
   */
    videoDialogPlayer.pause();

    videoDialogPlayer.src =
      button.dataset.video || "";

    videoDialogPlayer.poster =
      button.dataset.poster || "";

    videoDialogPlayer.load();

    if (videoDialogTitle) {
      videoDialogTitle.textContent =
        button.dataset.title || "";
    }

    if (videoDialogCounter) {
      videoDialogCounter.textContent =
        `${index + 1} / ${videoDialogList.length}`;
    }

    if (videoDialogPrev) {
      videoDialogPrev.disabled =
        index === 0;
    }

    if (videoDialogNext) {
      videoDialogNext.disabled =
        index === videoDialogList.length - 1;
    }
  }


  document.addEventListener("click", (event) => {
    const button =
      event.target.closest(".video-open");

    if (!button || !videoDialog) {
      return;
    }

    videoDialogList =
      getVideoDialogItems();

    videoDialogIndex =
      videoDialogList.indexOf(button);

    if (videoDialogIndex === -1) {
      return;
    }

    showDialogVideo(videoDialogIndex);

    if (!videoDialog.open) {
      lockVideoDialogScroll();

      videoDialog.showModal();

      videoDialog.focus({
        preventScroll: true,
      });
    }
  });


  videoDialogPrev?.addEventListener(
    "click",
    () => {
      showDialogVideo(
        videoDialogIndex - 1
      );
    }
  );


  videoDialogNext?.addEventListener(
    "click",
    () => {
      showDialogVideo(
        videoDialogIndex + 1
      );
    }
  );


  videoDialogClose?.addEventListener(
    "click",
    () => {
      videoDialog?.close();
    }
  );

  videoDialog?.addEventListener("click", (event) => {
    if (event.target === videoDialog) {
      videoDialog.close();
    }
  });


  videoDialog?.addEventListener(
    "close",
    () => {
      if (videoDialogPlayer) {
        videoDialogPlayer.pause();

        videoDialogPlayer.removeAttribute("src");
        videoDialogPlayer.removeAttribute("poster");

        videoDialogPlayer.load();
      }

      if (videoDialogTitle) {
        videoDialogTitle.textContent = "";
      }

      videoDialogList = [];

      unlockVideoDialogScroll();
    }
  );

  document.addEventListener(
    "keydown",
    (event) => {
      if (!videoDialog?.open) {
        return;
      }

      if (event.key === "ArrowLeft") {
        event.preventDefault();

        showDialogVideo(
          videoDialogIndex - 1
        );
      }

      if (event.key === "ArrowRight") {
        event.preventDefault();

        showDialogVideo(
          videoDialogIndex + 1
        );
      }
    }
  );
})();