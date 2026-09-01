// Toutou Crew — interactions du site
// Tarifs estimés pour 2 chiens (non capturés dans le Figma) : à corriger avec les vrais chiffres.

// Google Analytics : chargé uniquement après consentement (RGPD)
(function () {
  const CONSENT_KEY = "toutoucrew_analytics_consent";
  const GA_ID = "G-2B8ETLDWL5";

  function loadGA() {
    const script = document.createElement("script");
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    script.async = true;
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };
    window.gtag("js", new Date());
    window.gtag("config", GA_ID);
  }

  function init() {
    const banner = document.getElementById("cookie-banner");
    const acceptBtn = document.getElementById("cookie-accept");
    const refuseBtn = document.getElementById("cookie-refuse");
    const consent = localStorage.getItem(CONSENT_KEY);

    if (consent === "accepted") {
      loadGA();
    } else if (!consent && banner) {
      banner.classList.add("is-visible");
      banner.setAttribute("aria-hidden", "false");
    }

    acceptBtn?.addEventListener("click", () => {
      localStorage.setItem(CONSENT_KEY, "accepted");
      banner.classList.remove("is-visible");
      banner.setAttribute("aria-hidden", "true");
      loadGA();
    });

    refuseBtn?.addEventListener("click", () => {
      localStorage.setItem(CONSENT_KEY, "refused");
      banner.classList.remove("is-visible");
      banner.setAttribute("aria-hidden", "true");
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();

document.addEventListener("DOMContentLoaded", () => {
  // Animation de construction du hero au chargement
  const heroIntroEls = [
    { el: document.querySelector(".hero__image"), delay: 0 },
    { el: document.querySelector(".hero__title"), delay: 250 },
    { el: document.querySelector(".hero__eyebrow"), delay: 400 },
    { el: document.querySelector(".hero__text"), delay: 500 },
    { el: document.querySelector(".hero__sticker"), delay: 550 },
    { el: document.querySelector(".hero__content .button-row"), delay: 600 },
    { el: document.querySelector(".site-nav-bar"), delay: 800 },
  ];

  // Animation de construction du header du blog au chargement
  const blogIntroEls = [
    { el: document.querySelector(".blog-page__illustration"), delay: 0 },
    { el: document.querySelector(".blog-page__eyebrow"), delay: 200 },
    { el: document.querySelector(".blog-page__header h1"), delay: 350 },
    { el: document.querySelector(".blog-page__intro-text"), delay: 500 },
    { el: document.querySelector(".blog-featured"), delay: 700 },
  ];

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReducedMotion) {
    heroIntroEls.forEach(({ el }) => el && el.classList.add("is-visible"));
    blogIntroEls.forEach(({ el }) => el && el.classList.add("is-visible"));
  } else {
    requestAnimationFrame(() => {
      heroIntroEls.forEach(({ el, delay }) => {
        if (!el) return;
        setTimeout(() => el.classList.add("is-visible"), delay);
      });
      blogIntroEls.forEach(({ el, delay }) => {
        if (!el) return;
        setTimeout(() => el.classList.add("is-visible"), delay);
      });
    });
  }

  const pricingData = {
    1: [
      { frequence: "1 balade / semaine", detail: "(~4 par mois)", prix: "140€" },
      { frequence: "2 balades / semaine", detail: "(~8 par mois)", prix: "270€" },
      { frequence: "3 balades / semaine", detail: "(~12 par mois)", prix: "390€" },
      { frequence: "4 balades / semaine", detail: "", prix: "510€" },
      { frequence: "5 balades / semaine", detail: "", prix: "625€" },
    ],
    2: [
      { frequence: "1 balade / semaine", detail: "(~4 par mois)", prix: "250€" },
      { frequence: "2 balades / semaine", detail: "(~8 par mois)", prix: "485€" },
      { frequence: "3 balades / semaine", detail: "(~12 par mois)", prix: "700€" },
      { frequence: "4 balades / semaine", detail: "", prix: "920€" },
      { frequence: "5 balades / semaine", detail: "", prix: "1125€" },
    ],
  };

  const pricingBody = document.getElementById("pricing-body");
  const pricingImage = document.getElementById("pricing-image");
  const toggleButtons = document.querySelectorAll(".pricing__toggle-btn");

  const pricingImages = {
    1: { src: "images/chienseul.png", alt: "Illustration d'un chien assis sur une souche" },
    2: { src: "images/chienaccompagne.png", alt: "Illustration d'un chien assis sur une souche et d'un autre qui lui saute dessus pour s'amuser" },
  };

  function renderPricing(dogCount) {
    if (!pricingBody) return;
    pricingBody.innerHTML = "";
    pricingData[dogCount].forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.frequence} ${row.detail ? `<span style="color:var(--color-text-light); font-weight:400;">${row.detail}</span>` : ""}</td>
        <td>${row.prix}</td>
      `;
      pricingBody.appendChild(tr);
    });

    if (pricingImage) {
      pricingImage.src = pricingImages[dogCount].src;
      pricingImage.alt = pricingImages[dogCount].alt;
    }
  }

  toggleButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      toggleButtons.forEach((b) => {
        b.classList.remove("is-active");
        b.setAttribute("aria-pressed", "false");
      });
      btn.classList.add("is-active");
      btn.setAttribute("aria-pressed", "true");
      renderPricing(btn.dataset.dogs);
    });
  });

  renderPricing(1);

  // Barre de navigation : se cache en scrollant vers le bas, réapparaît en scrollant vers le haut
  const navBar = document.querySelector(".site-nav-bar");
  if (navBar) {
    let lastScrollY = window.scrollY;
    window.addEventListener(
      "scroll",
      () => {
        const currentScrollY = window.scrollY;
        const delta = currentScrollY - lastScrollY;
        if (Math.abs(delta) < 5) return;
        if (delta > 0 && currentScrollY > 100) {
          navBar.classList.add("is-hidden");
        } else if (delta < 0) {
          navBar.classList.remove("is-hidden");
        }
        lastScrollY = currentScrollY;
      },
      { passive: true }
    );
  }

  // Menu burger (mobile/tablette)
  const navEl = document.querySelector(".site-nav");
  const burger = document.querySelector(".site-nav__burger");
  if (navEl && burger) {
    const closeMenu = () => {
      navEl.classList.remove("is-open");
      burger.classList.remove("is-active");
      burger.setAttribute("aria-expanded", "false");
    };

    burger.addEventListener("click", () => {
      const isOpen = navEl.classList.toggle("is-open");
      burger.classList.toggle("is-active", isOpen);
      burger.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    navEl.querySelectorAll(".site-nav__links a").forEach((link) => {
      link.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && navEl.classList.contains("is-open")) {
        closeMenu();
        burger.focus();
      }
    });
  }

  // Effets d'apparition au scroll (blocs + images)
  const blockSelectors = [
    ".split",
    ".compagnon-card .section__intro",
    ".card-grid > .card",
    ".journee-card > h2",
    ".timeline__item",
    ".etapes-card .section__intro",
    ".step",
    ".tarifs-card .section__intro",
    ".pricing__toggle",
    ".pricing__panel",
    ".about__text",
    ".certifications",
    ".final-cta",
    ".blog-grid > .blog-card",
    ".article-page__meta",
    ".article-page__title",
    ".article-page__body",
  ];

  document.querySelectorAll(blockSelectors.join(", ")).forEach((el) => {
    el.classList.add("reveal");
  });

  const imageIconClasses = ["titre-icon", "pricing__toggle-icon", "step__icon", "blog-page__illustration"];

  document.querySelectorAll("main img, footer img").forEach((img) => {
    if (imageIconClasses.some((cls) => img.classList.contains(cls))) return;
    img.classList.add("reveal-img");
  });

  const revealables = document.querySelectorAll(".reveal, .reveal-img");

  if (revealables.length) {
    // Système volontairement simple (calcul manuel de position plutôt qu'un
    // IntersectionObserver avec seuil/marge négative) : plus prévisible d'un
    // appareil à l'autre, et impossible de laisser un élément bloqué invisible.
    const pending = new Set(revealables);

    const revealIfVisible = () => {
      pending.forEach((el) => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 60 && rect.bottom > 0) {
          el.classList.add("is-visible");
          pending.delete(el);
        }
      });
      if (pending.size === 0) {
        window.removeEventListener("scroll", revealIfVisible);
        window.removeEventListener("resize", revealIfVisible);
      }
    };

    // Les éléments déjà visibles à l'écran au chargement (avant tout scroll)
    // sont révélés tout de suite, en cascade, plutôt que d'attendre un scroll
    // qui ne viendra peut-être jamais (ça laissait un blanc en haut de page).
    // Le décalage de départ laisse d'abord finir l'animation d'en-tête du blog
    // (illustration/eyebrow/titre/description/carte à la une, jusqu'à 700ms).
    let visibleIndex = 0;
    const alreadyVisibleBaseDelay = document.querySelector(".blog-featured") ? 750 : 0;
    revealables.forEach((el) => {
      const rect = el.getBoundingClientRect();
      const alreadyVisible = rect.top < window.innerHeight && rect.bottom > 0;
      if (alreadyVisible) {
        const delay = alreadyVisibleBaseDelay + visibleIndex * 100;
        visibleIndex += 1;
        pending.delete(el);
        requestAnimationFrame(() => {
          setTimeout(() => el.classList.add("is-visible"), delay);
        });
      }
    });

    if (pending.size) {
      window.addEventListener("scroll", revealIfVisible, { passive: true });
      window.addEventListener("resize", revealIfVisible);
      // Filet de sécurité : si un élément n'a toujours pas été révélé après
      // quelques secondes (orientation, appareil qui ne déclenche pas le
      // scroll comme attendu...), on l'affiche quand même plutôt que de le
      // laisser invisible pour de bon.
      setTimeout(() => {
        pending.forEach((el) => el.classList.add("is-visible"));
        pending.clear();
      }, 4000);
    }
  }
});
