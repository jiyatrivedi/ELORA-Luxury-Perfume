// ELORA — Luxury Perfume E-commerce Script
// Enhanced: Preloader, Hero Floating Parallax, GSAP/Scroll Reveals,
// Real-time Search & Filters, Cart Sync, Animated Add-to-Bag

(function () {
  "use strict";

  /* =============================================
     1. PRELOADER
     ============================================= */
  var preloader = document.getElementById("elora-preloader");
  function dismissPreloader() {
    if (preloader) {
      preloader.classList.add("fade-out");
      setTimeout(function () {
        preloader.style.display = "none";
      }, 800);
    }
  }
  if (document.readyState === "complete") {
    setTimeout(dismissPreloader, 350);
  } else {
    window.addEventListener("load", function () {
      setTimeout(dismissPreloader, 350);
    });
  }
  // Safety timeout in case an asset hangs
  setTimeout(dismissPreloader, 2500);

  /* =============================================
     2. GLOBAL CART STATE & HELPERS
     ============================================= */
  var cartItems = [];
  var cartCountBadge = document.getElementById("cart-count");
  var cartBtn = document.getElementById("cart-btn");
  var bagToast = document.getElementById("bag-toast");
  var bagToastMsg = document.getElementById("bag-toast-msg");
  var toastTimer = null;

  function loadCart() {
    try {
      var stored = localStorage.getItem("elora_bag");
      if (stored) {
        cartItems = JSON.parse(stored) || [];
      }
    } catch (e) {
      cartItems = [];
    }
    updateCartUI();
  }

  function saveCart() {
    try {
      localStorage.setItem("elora_bag", JSON.stringify(cartItems));
    } catch (e) {}
  }

  function updateCartUI() {
    var total = cartItems.reduce(function (sum, item) {
      return sum + (Number(item.qty) || 0);
    }, 0);

    if (cartCountBadge) {
      cartCountBadge.textContent = total;
      cartCountBadge.setAttribute("aria-label", total + " items in bag");
      if (total > 0) {
        cartCountBadge.classList.add("visible");
      } else {
        cartCountBadge.classList.remove("visible");
      }
    }
  }

  function animateCartIcon() {
    if (!cartBtn) return;
    cartBtn.classList.remove("pop");
    void cartBtn.offsetWidth; // force reflow
    cartBtn.classList.add("pop");
    setTimeout(function () {
      cartBtn.classList.remove("pop");
    }, 600);
  }

  function showToast(message) {
    if (!bagToast || !bagToastMsg) return;
    if (toastTimer) {
      clearTimeout(toastTimer);
      toastTimer = null;
      bagToast.classList.remove("show");
    }
    bagToastMsg.textContent = message;
    void bagToast.offsetWidth;
    bagToast.classList.add("show");
    toastTimer = setTimeout(function () {
      bagToast.classList.remove("show");
      toastTimer = null;
    }, 3800);
  }

  window.eloraAddToCart = function (productId, productName, qty) {
    qty = Number(qty) || 1;
    var existing = null;
    for (var i = 0; i < cartItems.length; i++) {
      if (cartItems[i].id === productId) {
        existing = cartItems[i];
        break;
      }
    }
    if (existing) {
      existing.qty += qty;
    } else {
      cartItems.push({ id: productId, name: productName, qty: qty });
    }
    saveCart();
    updateCartUI();
    animateCartIcon();
    showToast((productName || "Fragrance") + " added to your bag.");
  };

  loadCart();

  /* =============================================
     3. NAVBAR & SCROLL BEHAVIOR
     ============================================= */
  var navbar = document.getElementById("navbar");
  var menuBtn = document.getElementById("menu-btn");
  var mobileMenu = document.getElementById("mobile-menu");
  var sections = document.querySelectorAll("section[id]");
  var navLinks = document.querySelectorAll(".nav-link");

  function handleScroll() {
    if (!navbar) return;
    if (window.scrollY > 30) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
    setActiveNavLink();
  }

  function setActiveNavLink() {
    if (!sections.length || !navLinks.length) return;
    var current = "";
    var scrollY = window.scrollY;
    var offset = navbar ? navbar.offsetHeight + 90 : 100;

    sections.forEach(function (sec) {
      var top = sec.offsetTop - offset;
      if (scrollY >= top) {
        current = sec.getAttribute("id");
      }
    });

    navLinks.forEach(function (link) {
      link.classList.remove("active");
      var href = link.getAttribute("href");
      if (href && href.replace("#", "") === current) {
        link.classList.add("active");
      }
    });
  }

  window.addEventListener("scroll", handleScroll, { passive: true });
  handleScroll();

  // Mobile menu
  function closeMobileMenu() {
    if (menuBtn && mobileMenu) {
      menuBtn.classList.remove("open");
      mobileMenu.classList.remove("open");
      menuBtn.setAttribute("aria-expanded", "false");
      mobileMenu.setAttribute("aria-hidden", "true");
    }
  }

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      var isOpen = mobileMenu.classList.contains("open");
      if (isOpen) {
        closeMobileMenu();
      } else {
        menuBtn.classList.add("open");
        mobileMenu.classList.add("open");
        menuBtn.setAttribute("aria-expanded", "true");
        mobileMenu.setAttribute("aria-hidden", "false");
      }
    });

    document.querySelectorAll(".mobile-nav-link").forEach(function (l) {
      l.addEventListener("click", closeMobileMenu);
    });

    document.addEventListener("click", function (e) {
      if (mobileMenu.classList.contains("open") && !mobileMenu.contains(e.target) && !menuBtn.contains(e.target)) {
        closeMobileMenu();
      }
    });
  }

  // Smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener("click", function (e) {
      var targetId = this.getAttribute("href");
      if (!targetId || targetId === "#") return;
      var target = document.querySelector(targetId);
      if (!target) return;
      e.preventDefault();
      var navHeight = navbar ? navbar.offsetHeight : 80;
      var top = target.getBoundingClientRect().top + window.scrollY - navHeight - 16;
      window.scrollTo({ top: top, behavior: "smooth" });
      closeMobileMenu();
    });
  });

  /* =============================================
     4. HERO SECTION — PARALLAX & FLOATING BOTTLE
     ============================================= */
  var heroSection = document.getElementById("home");
  var heroBottle = document.getElementById("hero-main-bottle");
  var heroAura = document.getElementById("hero-aura");

  if (heroSection && heroBottle) {
    heroSection.addEventListener("mousemove", function (e) {
      var rect = heroSection.getBoundingClientRect();
      var x = (e.clientX - rect.left) / rect.width - 0.5;
      var y = (e.clientY - rect.top) / rect.height - 0.5;

      var tiltX = y * 14;
      var tiltY = -x * 18;
      var shiftX = x * 22;
      var shiftY = y * 22;

      heroBottle.style.transform = "translate(" + shiftX + "px, " + shiftY + "px) rotateX(" + tiltX + "deg) rotateY(" + tiltY + "deg)";
      if (heroAura) {
        heroAura.style.transform = "translate(calc(-50% + " + (x * 30) + "px), calc(-50% + " + (y * 30) + "px)) scale(1.08)";
      }
    });

    heroSection.addEventListener("mouseleave", function () {
      heroBottle.style.transform = "translate(0px, 0px) rotateX(0deg) rotateY(0deg)";
      if (heroAura) {
        heroAura.style.transform = "translate(-50%, -50%) scale(1)";
      }
    });
  }

  /* =============================================
     5. SCROLL REVEALS & STATS COUNTER
     ============================================= */
  function setupScrollReveals() {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll(".reveal, .reveal-right, .reveal-card").forEach(function (el) {
      observer.observe(el);
    });

    // Story section number counters
    var statsObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateStats();
          statsObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });

    var storyStats = document.querySelector(".story-stats");
    if (storyStats) {
      statsObserver.observe(storyStats);
    }
  }

  function animateStats() {
    var statNums = document.querySelectorAll(".stat-number[data-target]");
    statNums.forEach(function (el) {
      var target = parseInt(el.getAttribute("data-target"), 10);
      var suffix = el.getAttribute("data-suffix") || "";
      var start = 0;
      var duration = 1600;
      var startTime = null;

      function step(timestamp) {
        if (!startTime) startTime = timestamp;
        var progress = Math.min((timestamp - startTime) / duration, 1);
        var current = Math.floor(progress * target);
        el.textContent = current + (progress === 1 ? suffix : "");
        if (progress < 1) {
          requestAnimationFrame(step);
        }
      }
      requestAnimationFrame(step);
    });
  }

  setupScrollReveals();

  /* =============================================
     6. PRODUCT COLLECTION SEARCH & FILTERS
     ============================================= */
  var searchInput = document.getElementById("collection-search");
  var searchClearBtn = document.getElementById("search-clear");
  var categoryBtns = document.querySelectorAll(".category-pill-btn");
  var sortDropdown = document.getElementById("collection-sort");
  var cardsGrid = document.getElementById("cards-grid");
  var productCards = document.querySelectorAll(".product-card[data-product]");
  var noResultsCard = document.getElementById("no-results-card");
  var resetSearchBtn = document.getElementById("reset-search-btn");
  var resultsCountEl = document.getElementById("results-count");

  var activeCategory = "all";
  var currentSearchQuery = "";
  var currentSort = "featured";

  function filterAndSortProducts() {
    if (!productCards.length) return;
    var visibleCount = 0;
    var cardsArray = Array.prototype.slice.call(productCards);

    cardsArray.forEach(function (card) {
      var name = (card.dataset.name || "").toLowerCase();
      var cat = (card.dataset.category || "").toLowerCase();
      var family = (card.dataset.family || "").toLowerCase();
      var notes = (card.dataset.notes || "").toLowerCase();
      var desc = (card.dataset.description || "").toLowerCase();

      var matchesCategory = (activeCategory === "all") ||
        (family.indexOf(activeCategory) !== -1) ||
        (cat.indexOf(activeCategory) !== -1);

      var matchesSearch = !currentSearchQuery ||
        (name.indexOf(currentSearchQuery) !== -1) ||
        (notes.indexOf(currentSearchQuery) !== -1) ||
        (family.indexOf(currentSearchQuery) !== -1) ||
        (desc.indexOf(currentSearchQuery) !== -1);

      if (matchesCategory && matchesSearch) {
        card.style.display = "";
        card.classList.add("visible");
        visibleCount++;
      } else {
        card.style.display = "none";
      }
    });

    // Sorting
    if (cardsGrid) {
      cardsArray.sort(function (a, b) {
        var priceA = parseFloat(a.dataset.price || 0);
        var priceB = parseFloat(b.dataset.price || 0);
        var ratingA = parseFloat(a.dataset.rating || 0);
        var ratingB = parseFloat(b.dataset.rating || 0);

        if (currentSort === "price-asc") return priceA - priceB;
        if (currentSort === "price-desc") return priceB - priceA;
        if (currentSort === "rating") return ratingB - ratingA;
        return (parseInt(a.dataset.index || 0, 10)) - (parseInt(b.dataset.index || 0, 10));
      });

      cardsArray.forEach(function (c) {
        cardsGrid.appendChild(c);
      });
    }

    if (resultsCountEl) {
      resultsCountEl.textContent = visibleCount + (visibleCount === 1 ? " fragrance" : " fragrances");
    }

    if (noResultsCard) {
      noResultsCard.classList.toggle("visible", visibleCount === 0);
    }
  }

  if (searchInput) {
    searchInput.addEventListener("input", function () {
      currentSearchQuery = this.value.trim().toLowerCase();
      if (searchClearBtn) {
        searchClearBtn.classList.toggle("visible", currentSearchQuery.length > 0);
      }
      filterAndSortProducts();
    });
  }

  if (searchClearBtn) {
    searchClearBtn.addEventListener("click", function () {
      if (searchInput) {
        searchInput.value = "";
        currentSearchQuery = "";
      }
      searchClearBtn.classList.remove("visible");
      filterAndSortProducts();
    });
  }

  categoryBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      categoryBtns.forEach(function (b) { b.classList.remove("active"); });
      this.classList.add("active");
      activeCategory = (this.dataset.category || "all").toLowerCase();
      filterAndSortProducts();
    });
  });

  if (sortDropdown) {
    sortDropdown.addEventListener("change", function () {
      currentSort = this.value;
      filterAndSortProducts();
    });
  }

  if (resetSearchBtn) {
    resetSearchBtn.addEventListener("click", function () {
      if (searchInput) searchInput.value = "";
      currentSearchQuery = "";
      activeCategory = "all";
      categoryBtns.forEach(function (b) {
        b.classList.toggle("active", b.dataset.category === "all");
      });
      if (sortDropdown) sortDropdown.value = "featured";
      currentSort = "featured";
      if (searchClearBtn) searchClearBtn.classList.remove("visible");
      filterAndSortProducts();
    });
  }

  /* =============================================
     7. CARD DIRECT ADD TO BAG BUTTONS
     ============================================= */
  document.querySelectorAll(".btn-card-add-bag, .btn-card-quick-add").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var card = this.closest(".product-card");
      if (!card) return;
      var pid = card.dataset.product;
      var pname = card.dataset.name || "ELORA Fragrance";

      var label = this.querySelector(".btn-add-label");
      var self = this;
      this.classList.add("added-active");
      if (label) {
        label.textContent = "Added \u2713";
      } else {
        var originalText = this.innerHTML;
        this.innerHTML = "<span>Added \u2713</span>";
      }

      setTimeout(function () {
        self.classList.remove("added-active");
        if (label) {
          label.textContent = "Add to Bag";
        } else {
          self.innerHTML = originalText;
        }
      }, 1400);

      window.eloraAddToCart(pid, pname, 1);
    });
  });

  /* =============================================
     8. PRODUCT IN-PAGE DRAWER / DETAIL VIEWER
     ============================================= */
  var productDetail = document.getElementById("product-detail");
  var pdBackBtn = document.getElementById("pd-back-btn");
  var pdName = document.getElementById("pd-name");
  var pdCategory = document.getElementById("pd-category");
  var pdTagline = document.getElementById("pd-tagline");
  var pdNotesPills = document.getElementById("pd-notes-pills");
  var pdDescription = document.getElementById("pd-description");
  var pdPrice = document.getElementById("pd-price");
  var pdGlow = document.getElementById("pd-glow");
  var pdProductImage = document.getElementById("pd-product-image");
  var pdFullPageLink = document.getElementById("pd-full-page-link");
  var qtyMinus = document.getElementById("qty-minus");
  var qtyPlus = document.getElementById("qty-plus");
  var qtyVal = document.getElementById("qty-val");
  var btnAddBag = document.getElementById("btn-add-bag");

  var currentProductData = null;
  var currentQuantity = 1;

  function openProductDetail(productKey) {
    var card = document.querySelector('.product-card[data-product="' + productKey + '"]');
    if (!card) return;

    var name = card.dataset.name;
    var price = "$" + parseInt(card.dataset.price || 0, 10);
    var category = card.dataset.category || "Eau de Parfum";
    var tagline = card.dataset.tagline || "";
    var desc = card.dataset.description || "";
    var notesStr = card.dataset.notes || "";
    var image = card.dataset.image || "/static/images/elora-hero.png";

    currentProductData = {
      id: productKey,
      name: name,
      price: price,
      category: category,
      image: image
    };
    currentQuantity = 1;
    if (qtyVal) qtyVal.textContent = "1";

    if (pdName) pdName.textContent = name;
    if (pdCategory) pdCategory.textContent = category;
    if (pdTagline) pdTagline.textContent = tagline;
    if (pdDescription) pdDescription.textContent = desc;
    if (pdPrice) pdPrice.textContent = price;
    if (pdProductImage) {
      pdProductImage.src = image;
      pdProductImage.alt = name;
    }
    if (pdFullPageLink) {
      pdFullPageLink.href = "/product/" + productKey;
    }

    if (pdNotesPills) {
      pdNotesPills.innerHTML = "";
      var notes = notesStr.split("·");
      notes.forEach(function (n) {
        var pill = document.createElement("span");
        pill.className = "pd-note-pill";
        pill.textContent = n.trim();
        pdNotesPills.appendChild(pill);
      });
    }

    if (pdGlow) {
      pdGlow.className = "pd-glow glow-" + productKey;
    }

    if (productDetail) {
      productDetail.setAttribute("aria-hidden", "false");
      productDetail.classList.add("active");
      requestAnimationFrame(function () {
        var navHeight = navbar ? navbar.offsetHeight : 80;
        var top = productDetail.getBoundingClientRect().top + window.scrollY - navHeight - 16;
        window.scrollTo({ top: top, behavior: "smooth" });
        setTimeout(function () {
          productDetail.classList.add("visible");
        }, 120);
      });
    }
  }

  function closeProductDetail() {
    if (!productDetail) return;
    productDetail.classList.remove("visible");
    setTimeout(function () {
      productDetail.classList.remove("active");
      productDetail.setAttribute("aria-hidden", "true");
      currentProductData = null;
      var collection = document.getElementById("collection");
      if (collection) {
        var navHeight = navbar ? navbar.offsetHeight : 80;
        var top = collection.getBoundingClientRect().top + window.scrollY - navHeight - 16;
        window.scrollTo({ top: top, behavior: "smooth" });
      }
    }, 450);
  }

  // Wire DISCOVER buttons
  document.querySelectorAll(".btn-discover").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var card = this.closest(".product-card");
      if (card) openProductDetail(card.dataset.product);
    });
  });

  if (pdBackBtn) {
    pdBackBtn.addEventListener("click", closeProductDetail);
  }

  if (qtyMinus) {
    qtyMinus.addEventListener("click", function () {
      if (currentQuantity > 1) {
        currentQuantity--;
        if (qtyVal) qtyVal.textContent = currentQuantity;
      }
    });
  }

  if (qtyPlus) {
    qtyPlus.addEventListener("click", function () {
      if (currentQuantity < 10) {
        currentQuantity++;
        if (qtyVal) qtyVal.textContent = currentQuantity;
      }
    });
  }

  if (btnAddBag) {
    btnAddBag.addEventListener("click", function () {
      if (!currentProductData) return;
      window.eloraAddToCart(currentProductData.id, currentProductData.name, currentQuantity);
    });
  }

  /* =============================================
     9. VIP CLUB / NEWSLETTER COUPON REWARD
     ============================================= */
  var newsletterForm = document.getElementById("vip-newsletter-form");
  var vipRewardModal = document.getElementById("vip-reward-banner");
  if (newsletterForm) {
    newsletterForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var emailInput = document.getElementById("vip-email");
      if (emailInput && emailInput.value.indexOf("@") !== -1) {
        if (vipRewardModal) {
          vipRewardModal.style.display = "block";
          vipRewardModal.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
        showToast("Welcome to the ELORA VIP Atelier. Privilege code ELORA10 unlocked.");
        emailInput.value = "";
      }
    });
  }

  console.log("ELORA: script.js v2.0 initialized.");
})();
