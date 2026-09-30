// Page-load progress bar — shows instant feedback on navigation clicks,
// then completes as soon as this script runs on the newly-loaded page.
(function () {
    var bar = document.getElementById('pageLoaderBar');
    if (!bar) return;

    requestAnimationFrame(function () {
        bar.style.width = '100%';
        setTimeout(function () { bar.classList.add('done'); }, 200);
    });

    window.addEventListener('pageshow', function (e) {
        if (e.persisted) {
            bar.classList.remove('done');
            bar.style.width = '100%';
            setTimeout(function () { bar.classList.add('done'); }, 150);
        }
    });

    document.addEventListener('click', function (e) {
        var link = e.target.closest('a');
        if (!link || e.defaultPrevented || e.ctrlKey || e.metaKey || e.shiftKey) return;
        if (link.target === '_blank' || link.hasAttribute('download')) return;
        var href = link.getAttribute('href');
        if (!href || href.charAt(0) === '#' || href.indexOf('mailto:') === 0 || href.indexOf('tel:') === 0 || href.indexOf('javascript:') === 0) return;
        if (link.origin !== window.location.origin) return;
        if (link.pathname === window.location.pathname && link.hash) return;

        // Defer so handlers that cancel navigation (e.g. the mobile Services
        // accordion) get to call preventDefault() before the bar starts.
        setTimeout(function () {
            if (e.defaultPrevented) return;
            bar.classList.remove('done');
            bar.style.width = '0%';
            requestAnimationFrame(function () {
                requestAnimationFrame(function () { bar.style.width = '75%'; });
            });
        }, 0);
    }, true);
})();

document.addEventListener('DOMContentLoaded', function () {
    // 00. Smooth inertial scrolling (Lenis) — public site only, desktop pointers only,
    //     never when the visitor prefers reduced motion. Touch devices keep native scrolling.
    (function initSmoothScroll() {
        if (!window.Lenis || !document.getElementById('mainNavbar')) return;
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        if (!window.matchMedia('(pointer: fine)').matches) return;
        const lenis = new window.Lenis({ lerp: 0.1, wheelMultiplier: 1, smoothWheel: true });
        window.tmLenis = lenis;
        function raf(time) {
            lenis.raf(time);
            requestAnimationFrame(raf);
        }
        requestAnimationFrame(raf);
    })();

    // 0. Scroll-Reveal System
    const revealEls = document.querySelectorAll('.animate-on-scroll');
    if (revealEls.length > 0) {
        if ('IntersectionObserver' in window) {
            const revealObserver = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('in-view');
                        revealObserver.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });
            revealEls.forEach((el) => revealObserver.observe(el));
        } else {
            revealEls.forEach((el) => el.classList.add('in-view'));
        }
    }

    // 1. Navbar — scroll state, docked progress bar, smooth anchor scroll,
    //    off-canvas mobile drawer with services accordion, desktop hover pill
    (function initNavbar() {
        const navbar = document.getElementById('mainNavbar');
        const mobileToggle = document.getElementById('mobileMenuToggle');
        const navContainer = document.getElementById('navbarNavContainer');
        const drawerClose = document.getElementById('drawerClose');
        const dropdownItems = Array.from(navContainer ? navContainer.querySelectorAll('.nav-item.has-dropdown') : []);
        const dropdownTriggers = dropdownItems.map((item) => item.querySelector(':scope > .nav-link'));
        const progressBar = document.getElementById('navProgressBar');
        const progressTrack = progressBar ? progressBar.parentElement : null;
        const mobileOverlay = document.querySelector('.mobile-overlay');
        const root = document.documentElement;
        const mobileQuery = window.matchMedia('(max-width: 1024px)');
        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

        if (!navbar || !mobileToggle || !navContainer) return;

        const isMobile = () => mobileQuery.matches;

        // Keep --nav-height in sync so scroll-padding / anchor offsets match the real bar
        function syncNavHeight() {
            root.style.setProperty('--nav-height', navbar.offsetHeight + 'px');
        }
        if ('ResizeObserver' in window) {
            new ResizeObserver(syncNavHeight).observe(navbar);
        }
        syncNavHeight();

        // Scroll state + progress, batched into one rAF per frame
        let ticking = false;
        function onScrollFrame() {
            const y = window.scrollY;
            navbar.classList.toggle('scrolled', y > 24);

            if (progressBar && progressTrack) {
                const max = root.scrollHeight - window.innerHeight;
                const ratio = max > 0 ? Math.min(Math.max(y / max, 0), 1) : 0;
                progressBar.style.transform = 'scaleX(' + ratio + ')';
                progressTrack.style.setProperty('--progress-x', (ratio * progressTrack.clientWidth) + 'px');
                progressTrack.style.setProperty('--progress-tip', ratio > 0.005 && ratio < 0.995 ? '1' : '0');
            }
            ticking = false;
        }
        function requestScrollFrame() {
            if (!ticking) {
                ticking = true;
                requestAnimationFrame(onScrollFrame);
            }
        }
        window.addEventListener('scroll', requestScrollFrame, { passive: true });
        window.addEventListener('resize', requestScrollFrame, { passive: true });
        window.addEventListener('load', requestScrollFrame);
        onScrollFrame();

        // Smooth-scroll same-page anchors, offset by the fixed navbar
        document.addEventListener('click', function (event) {
            const link = event.target.closest('a[href*="#"]');
            if (!link || event.defaultPrevented || link.origin !== window.location.origin || link.pathname !== window.location.pathname) return;
            const hash = link.hash;
            if (!hash || hash === '#') {
                if (link.classList.contains('back-to-top')) {
                    event.preventDefault();
                    if (window.tmLenis) window.tmLenis.scrollTo(0, { duration: 1.2 });
                    else window.scrollTo({ top: 0, behavior: reduceMotion.matches ? 'auto' : 'smooth' });
                }
                return;
            }
            let target = null;
            try { target = document.querySelector(decodeURIComponent(hash)); } catch (e) { return; }
            if (!target) return;
            event.preventDefault();
            closeMobileMenu(false);
            const top = target.getBoundingClientRect().top + window.scrollY - navbar.offsetHeight - 16;
            if (window.tmLenis) window.tmLenis.scrollTo(Math.max(top, 0), { duration: 1.2 });
            else window.scrollTo({ top: Math.max(top, 0), behavior: reduceMotion.matches ? 'auto' : 'smooth' });
            history.pushState(null, '', hash);
        });

        // --- Mobile drawer ---
        function setDropdownOpen(item, open) {
            item.classList.toggle('dropdown-open', open);
            item.querySelector(':scope > .nav-link')?.setAttribute('aria-expanded', open ? 'true' : 'false');
        }
        function closeAllDropdowns() {
            dropdownItems.forEach((item) => setDropdownOpen(item, false));
        }

        function openMobileMenu() {
            navContainer.classList.add('mobile-open');
            navbar.classList.add('menu-open');
            if (mobileOverlay) mobileOverlay.classList.add('active');
            root.classList.add('nav-locked');
            window.tmLenis?.stop();
            mobileToggle.setAttribute('aria-expanded', 'true');
            navContainer.setAttribute('role', 'dialog');
            navContainer.setAttribute('aria-modal', 'true');
            navContainer.setAttribute('aria-label', 'Site navigation');
            // Expand the section containing the current page
            dropdownItems.forEach((item) => {
                if (item.querySelector(':scope > .nav-link.active')) setDropdownOpen(item, true);
            });
            setTimeout(function () { (drawerClose || navContainer).focus({ preventScroll: true }); }, 60);
        }

        function closeMobileMenu(returnFocus) {
            if (!navContainer.classList.contains('mobile-open')) return;
            navContainer.classList.remove('mobile-open');
            navbar.classList.remove('menu-open');
            if (mobileOverlay) mobileOverlay.classList.remove('active');
            root.classList.remove('nav-locked');
            window.tmLenis?.start();
            mobileToggle.setAttribute('aria-expanded', 'false');
            navContainer.removeAttribute('role');
            navContainer.removeAttribute('aria-modal');
            navContainer.removeAttribute('aria-label');
            if (returnFocus !== false) mobileToggle.focus({ preventScroll: true });
        }

        mobileToggle.addEventListener('click', function (event) {
            event.stopPropagation();
            navContainer.classList.contains('mobile-open') ? closeMobileMenu() : openMobileMenu();
        });
        if (drawerClose) drawerClose.addEventListener('click', () => closeMobileMenu());
        if (mobileOverlay) mobileOverlay.addEventListener('click', () => closeMobileMenu());

        // On mobile each dropdown row is a pure accordion toggle (one open at a time);
        // the links inside it do the navigating
        dropdownItems.forEach((item, index) => {
            const trigger = dropdownTriggers[index];
            if (!trigger) return;
            trigger.addEventListener('click', function (event) {
                if (!isMobile()) return;
                event.preventDefault();
                const willOpen = !item.classList.contains('dropdown-open');
                closeAllDropdowns();
                setDropdownOpen(item, willOpen);
                if (willOpen) revealInDrawer(item);
            });
        });

        // Smoothly bring a just-opened section into view inside the drawer (short phones)
        const drawerList = document.getElementById('navbarNavList');
        function revealInDrawer(el) {
            if (!drawerList || !el || !isMobile()) return;
            setTimeout(function () {
                const listRect = drawerList.getBoundingClientRect();
                const elRect = el.getBoundingClientRect();
                if (elRect.top < listRect.top + 8 || elRect.bottom > listRect.bottom - 8) {
                    const top = drawerList.scrollTop + (elRect.top - listRect.top) - 12;
                    drawerList.scrollTo({ top: Math.max(top, 0), behavior: reduceMotion.matches ? 'auto' : 'smooth' });
                }
            }, 260);
        }

        // Per-category accordions inside Services (mobile) — one open at a time.
        // The whole row toggles; "Explore <category>" inside links to the category page.
        navContainer.querySelectorAll('.ms-mobile .category-title-wrap').forEach(function (row) {
            row.addEventListener('click', function (event) {
                if (!isMobile()) return;
                event.preventDefault();
                const category = row.closest('.mega-dropdown-category');
                const btn = row.querySelector('.category-toggle');
                const willOpen = !category.classList.contains('is-open');
                navContainer.querySelectorAll('.mega-dropdown-category.is-open').forEach(function (other) {
                    other.classList.remove('is-open');
                    other.querySelector('.category-toggle')?.setAttribute('aria-expanded', 'false');
                });
                category.classList.toggle('is-open', willOpen);
                btn?.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
                if (willOpen) revealInDrawer(category);
            });
        });

        // Any real navigation from inside the drawer closes it
        navContainer.addEventListener('click', function (event) {
            const link = event.target.closest('a');
            if (!link || !isMobile() || dropdownTriggers.includes(link) || link.closest('.category-title-wrap')) return;
            closeMobileMenu(false);
        });

        document.addEventListener('keydown', function (event) {
            if (!navContainer.classList.contains('mobile-open')) return;
            if (event.key === 'Escape') {
                closeMobileMenu();
                return;
            }
            // Keep Tab focus inside the open drawer
            if (event.key === 'Tab') {
                const focusables = Array.from(navContainer.querySelectorAll('a[href], button:not([disabled])'))
                    .filter((el) => el.offsetParent !== null);
                if (!focusables.length) return;
                const first = focusables[0];
                const last = focusables[focusables.length - 1];
                if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
                else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
            }
        });

        mobileQuery.addEventListener('change', function (e) {
            if (!e.matches) {
                closeMobileMenu(false);
                closeAllDropdowns();
            }
        });

        // --- Desktop: sliding hover pill behind nav links ---
        const navList = document.getElementById('navbarNavList');
        const indicator = document.getElementById('navIndicator');
        if (navList && indicator) {
            const links = Array.from(navList.querySelectorAll(':scope > .nav-item > .nav-link'));

            function moveIndicatorTo(el) {
                if (!el || isMobile()) return;
                const containerRect = navContainer.getBoundingClientRect();
                const linkRect = el.getBoundingClientRect();
                indicator.style.width = linkRect.width + 'px';
                indicator.style.transform = 'translateX(' + (linkRect.left - containerRect.left - 1) + 'px)';
                indicator.style.opacity = '1';
            }

            links.forEach((link) => {
                link.addEventListener('mouseenter', () => moveIndicatorTo(link));
                link.addEventListener('focus', () => moveIndicatorTo(link));
            });
            navList.addEventListener('mouseleave', () => { indicator.style.opacity = '0'; });
            window.addEventListener('resize', () => { indicator.style.opacity = '0'; });
        }

        // Services mega-menu: category rail switches the service panel on the right
        const msTabs = Array.from(navContainer.querySelectorAll('.ms-tab'));
        if (msTabs.length) {
            const msIndicator = navContainer.querySelector('.ms-tab-indicator');
            const msPanels = Array.from(navContainer.querySelectorAll('.ms-panel'));
            const msInitial = navContainer.querySelector('.ms-tab[data-ms-current]') || msTabs[0];
            let msHoverTimer = null;

            const activateTab = (tab) => {
                msTabs.forEach((t) => t.classList.toggle('is-active', t === tab));
                msPanels.forEach((panel) => panel.classList.toggle('is-active', panel.id === tab.dataset.msTab));
                if (msIndicator) {
                    msIndicator.style.height = tab.offsetHeight + 'px';
                    msIndicator.style.transform = 'translateY(' + tab.offsetTop + 'px)';
                    msIndicator.style.setProperty('--ms-accent', getComputedStyle(tab).getPropertyValue('--tab-color'));
                }
            };

            msTabs.forEach((tab, index) => {
                // Short hover intent so sweeping the pointer across the rail doesn't flicker panels
                tab.addEventListener('mouseenter', () => {
                    clearTimeout(msHoverTimer);
                    msHoverTimer = setTimeout(() => activateTab(tab), 70);
                });
                tab.addEventListener('mouseleave', () => clearTimeout(msHoverTimer));
                tab.addEventListener('focus', () => activateTab(tab));
                tab.addEventListener('keydown', (event) => {
                    if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
                    event.preventDefault();
                    const next = msTabs[(index + (event.key === 'ArrowDown' ? 1 : -1) + msTabs.length) % msTabs.length];
                    next.focus();
                });
            });

            activateTab(msInitial);
            const servicesMenuItem = msTabs[0].closest('.has-dropdown');
            if (servicesMenuItem) {
                servicesMenuItem.addEventListener('mouseenter', () => activateTab(msTabs.find((t) => t.classList.contains('is-active')) || msInitial));
                servicesMenuItem.addEventListener('mouseleave', () => setTimeout(() => {
                    if (!servicesMenuItem.matches(':hover, :focus-within')) activateTab(msInitial);
                }, 400));
            }
        }

        // Count-up for numeric stats in the About panel, the first time it opens
        const countEls = Array.from(navContainer.querySelectorAll('[data-countup]'));
        if (countEls.length && !reduceMotion.matches) {
            const targets = countEls.map((el) => {
                const match = el.textContent.trim().match(/^(\d+)(.*)$/);
                return match ? { el, end: parseInt(match[1], 10), suffix: match[2] } : null;
            }).filter(Boolean);
            let counted = false;
            const runCountUp = () => {
                if (counted || isMobile()) return;
                counted = true;
                const start = performance.now();
                const duration = 1100;
                targets.forEach((t) => { t.el.textContent = '0' + t.suffix; });
                (function frame(now) {
                    const progress = Math.min((now - start) / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    targets.forEach((t) => { t.el.textContent = Math.round(t.end * eased) + t.suffix; });
                    if (progress < 1) requestAnimationFrame(frame);
                })(start);
            };
            const panelOwner = countEls[0].closest('.has-dropdown');
            if (panelOwner) {
                panelOwner.addEventListener('mouseenter', runCountUp);
                panelOwner.addEventListener('focusin', runCountUp);
            }
        }

        // Mega-dropdown spotlight: dim sibling categories while one is hovered
        const megaGrid = document.getElementById('megaDropdownGrid');
        if (megaGrid && window.matchMedia('(pointer: fine)').matches) {
            megaGrid.querySelectorAll('.mega-dropdown-category').forEach((cat) => {
                cat.addEventListener('mouseenter', () => { if (!isMobile()) megaGrid.classList.add('has-focus'); });
            });
            megaGrid.addEventListener('mouseleave', () => megaGrid.classList.remove('has-focus'));
        }
    })();

    // 1b. Homepage hero carousel — the active tab's progress bar (CSS animation) is the timer
    (function initHeroCarousel() {
        const hero = document.getElementById('heroCarousel');
        if (!hero) return;
        const slides = Array.from(hero.querySelectorAll('[data-hc-slide]'));
        const backdrops = Array.from(hero.querySelectorAll('[data-hc-backdrop]'));
        const tabs = Array.from(hero.querySelectorAll('[data-hc-tab]'));
        const pauseBtn = hero.querySelector('[data-hc-pause]');
        if (slides.length < 2) return;

        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        hero.style.setProperty('--hc-interval', (parseInt(hero.dataset.interval, 10) || 7000) + 'ms');
        let index = 0;
        let userPaused = false;
        const pauseReasons = new Set();

        function syncPaused() {
            hero.classList.toggle('is-paused', userPaused || pauseReasons.size > 0);
        }
        function setReason(reason, on) {
            if (on) pauseReasons.add(reason); else pauseReasons.delete(reason);
            syncPaused();
        }

        function goTo(next) {
            next = (next + slides.length) % slides.length;
            if (next === index) return;
            const prev = slides[index];
            prev.classList.remove('is-active');
            prev.classList.add('is-leaving');
            prev.setAttribute('aria-hidden', 'true');
            prev.querySelectorAll('a').forEach((a) => a.setAttribute('tabindex', '-1'));
            setTimeout(() => prev.classList.remove('is-leaving'), 450);

            index = next;
            const slide = slides[index];
            slide.classList.add('is-active');
            slide.removeAttribute('aria-hidden');
            slide.querySelectorAll('a').forEach((a) => a.removeAttribute('tabindex'));
            backdrops.forEach((b, i) => b.classList.toggle('is-active', i === index));
            tabs.forEach((t, i) => {
                t.classList.toggle('is-active', i === index);
                t.setAttribute('aria-selected', i === index ? 'true' : 'false');
            });
        }

        tabs.forEach((tab, i) => {
            tab.addEventListener('click', () => goTo(i));
            tab.addEventListener('keydown', (e) => {
                if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
                e.preventDefault();
                const n = (i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
                tabs[n].focus();
                goTo(n);
            });
            tab.querySelector('.hc-tab-progress span')?.addEventListener('animationend', (e) => {
                if (e.animationName === 'hcProgress' && i === index) goTo(index + 1);
            });
        });
        hero.querySelector('[data-hc-prev]')?.addEventListener('click', () => goTo(index - 1));
        hero.querySelector('[data-hc-next]')?.addEventListener('click', () => goTo(index + 1));

        if (reduceMotion) {
            pauseBtn?.remove();
            return; // manual navigation only
        }
        hero.classList.add('is-playing');

        pauseBtn?.addEventListener('click', () => {
            userPaused = !userPaused;
            pauseBtn.innerHTML = userPaused ? '<i class="fas fa-play"></i>' : '<i class="fas fa-pause"></i>';
            pauseBtn.setAttribute('aria-label', userPaused ? 'Play slideshow' : 'Pause slideshow');
            syncPaused();
        });

        // Pause while the visitor is reading / interacting
        const main = hero.querySelector('.hc-main');
        if (window.matchMedia('(pointer: fine)').matches && main) {
            main.addEventListener('mouseenter', () => setReason('hover', true));
            main.addEventListener('mouseleave', () => setReason('hover', false));
        }
        hero.addEventListener('focusin', () => setReason('focus', true));
        hero.addEventListener('focusout', (e) => { if (!hero.contains(e.relatedTarget)) setReason('focus', false); });
        document.addEventListener('visibilitychange', () => setReason('hidden', document.hidden));
        if ('IntersectionObserver' in window) {
            new IntersectionObserver((entries) => {
                entries.forEach((entry) => setReason('offscreen', !entry.isIntersecting));
            }, { threshold: 0.25 }).observe(hero);
        }

        // Swipe on touch devices
        let startX = 0, startY = 0;
        hero.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; startY = e.touches[0].clientY; }, { passive: true });
        hero.addEventListener('touchend', (e) => {
            const dx = e.changedTouches[0].clientX - startX;
            const dy = e.changedTouches[0].clientY - startY;
            if (Math.abs(dx) > 50 && Math.abs(dy) < 60) goTo(index + (dx < 0 ? 1 : -1));
        }, { passive: true });
    })();

    // 2. Interactive Testimonial Carousel
    const track = document.querySelector('.carousel-track');
    const slides = document.querySelectorAll('.carousel-slide');
    const prevBtn = document.querySelector('.carousel-prev');
    const nextBtn = document.querySelector('.carousel-next');
    const dotsContainer = document.querySelector('.carousel-dots');

    if (track && slides.length > 0) {
        let currentIndex = 0;
        const totalSlides = slides.length;
        let autoSlideTimer = null;

        if (dotsContainer) {
            dotsContainer.innerHTML = '';
            slides.forEach((_, idx) => {
                const dot = document.createElement('div');
                dot.classList.add('carousel-dot');
                if (idx === 0) dot.classList.add('active');
                dot.addEventListener('click', () => {
                    goToSlide(idx);
                    resetAutoSlide();
                });
                dotsContainer.appendChild(dot);
            });
        }

        const updateDots = () => {
            const dots = document.querySelectorAll('.carousel-dot');
            dots.forEach((dot, idx) => {
                dot.classList.toggle('active', idx === currentIndex);
            });
        };

        const goToSlide = (index) => {
            currentIndex = (index + totalSlides) % totalSlides;
            track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';
            updateDots();
        };

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                goToSlide(currentIndex - 1);
                resetAutoSlide();
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                goToSlide(currentIndex + 1);
                resetAutoSlide();
            });
        }

        const startAutoSlide = () => {
            autoSlideTimer = setInterval(() => {
                goToSlide(currentIndex + 1);
            }, 4500);
        };

        const resetAutoSlide = () => {
            if (autoSlideTimer) clearInterval(autoSlideTimer);
            startAutoSlide();
        };

        if (track.parentElement) {
            track.parentElement.addEventListener('mouseenter', () => {
                if (autoSlideTimer) clearInterval(autoSlideTimer);
            });
            track.parentElement.addEventListener('mouseleave', () => {
                startAutoSlide();
            });
        }

        startAutoSlide();
    }

    // 2b. Tilt-on-hover for service & capability cards
    (function initCardTilt() {
        if (window.matchMedia('(pointer: coarse)').matches) return;
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

        const tiltCards = document.querySelectorAll('.service-card, .capability-card, .why-us-card');
        tiltCards.forEach((card) => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width - 0.5;
                const y = (e.clientY - rect.top) / rect.height - 0.5;
                card.style.transform = `perspective(1000px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg) translateY(-8px)`;
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
            });
        });
    })();

    // 3. Animated Metric Counters
    const counters = document.querySelectorAll('[data-counter]');
    if (counters.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const targetVal = parseInt(el.getAttribute('data-counter'), 10) || 0;
                    let currentVal = 0;
                    const step = Math.max(1, Math.ceil(targetVal / 40));
                    const timer = setInterval(() => {
                        currentVal += step;
                        if (currentVal >= targetVal) {
                            el.textContent = targetVal;
                            clearInterval(timer);
                        } else {
                            el.textContent = currentVal;
                        }
                    }, 30);
                    observer.unobserve(el);
                }
            });
        }, { threshold: 0.3 });

        counters.forEach(c => observer.observe(c));
    }

    // 4. Accordion Toggle (opens the item named in the URL hash, e.g. #faq-3 from search)
    if (location.hash && /^#faq-\d+$/.test(location.hash)) {
        const target = document.querySelector(location.hash);
        if (target && target.classList.contains('accordion-item')) {
            target.classList.add('open', 'in-view');
            setTimeout(() => target.scrollIntoView({ block: 'center' }), 50);
        }
    }
    document.querySelectorAll('.accordion-header').forEach((header) => {
        header.addEventListener('click', function () {
            const item = this.closest('.accordion-item');
            if (item) item.classList.toggle('open');
        });
    });

    // 6. Toasts — auto-dismiss + manual close
    function dismissToast(toast) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        setTimeout(() => toast.remove(), 300);
    }
    document.querySelectorAll('.toast').forEach((toast) => {
        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) closeBtn.addEventListener('click', () => dismissToast(toast));
        setTimeout(() => dismissToast(toast), 5000);
    });

    // 6c. Cookie Notice
    const cookieNotice = document.querySelector('.cookie-notice');
    if (cookieNotice) {
        try {
            if (!localStorage.getItem('tmsolutech_cookie_ack')) {
                setTimeout(() => cookieNotice.classList.add('visible'), 1200);
            }
        } catch (e) {
            setTimeout(() => cookieNotice.classList.add('visible'), 1200);
        }
        const acceptBtn = cookieNotice.querySelector('.cookie-accept');
        if (acceptBtn) {
            acceptBtn.addEventListener('click', () => {
                cookieNotice.classList.remove('visible');
                try { localStorage.setItem('tmsolutech_cookie_ack', '1'); } catch (e) {}
            });
        }
    }

    // 8. Executive Bio Modal Controller
    function initLeadershipBioModal() {
        const modal = document.getElementById('leaderBioModal');
        const backdrop = document.getElementById('leaderBioModalBackdrop');
        const closeBtn = document.getElementById('leaderBioModalClose');
        const modalImg = document.getElementById('modalLeaderImg');
        const modalRole = document.getElementById('modalLeaderRole');
        const modalName = document.getElementById('modalLeaderName');
        const modalBio = document.getElementById('modalLeaderBio');
        const modalSocials = document.getElementById('modalLeaderSocials');

        if (!modal) return;

        function closeModal() {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            window.tmLenis?.start();
        }

        function openModal(data) {
            if (modalImg) {
                modalImg.src = data.photo || '';
                modalImg.alt = data.name || 'Leader Photo';
            }
            if (modalRole) modalRole.textContent = data.designation || '';
            if (modalName) modalName.textContent = data.name || '';
            if (modalBio) modalBio.textContent = data.bio || 'Detailed biography coming soon.';

            if (modalSocials) {
                modalSocials.innerHTML = '';
                if (data.linkedin) {
                    modalSocials.innerHTML += `<a href="${data.linkedin}" target="_blank" rel="noopener noreferrer" class="social-circle linkedin" title="LinkedIn"><i class="fab fa-linkedin-in"></i></a>`;
                }
                if (data.email) {
                    modalSocials.innerHTML += `<a href="mailto:${data.email}" class="social-circle email" title="Email"><i class="fas fa-envelope"></i></a>`;
                }
            }

            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            window.tmLenis?.stop();
        }

        document.querySelectorAll('.open-bio-modal').forEach(btn => {
            const trigger = function (e) {
                e.stopPropagation();
                const data = {
                    name: this.getAttribute('data-name'),
                    designation: this.getAttribute('data-designation'),
                    photo: this.getAttribute('data-photo'),
                    linkedin: this.getAttribute('data-linkedin'),
                    email: this.getAttribute('data-email'),
                    bio: this.getAttribute('data-bio')
                };
                openModal(data);
            };
            btn.addEventListener('click', trigger);
            btn.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    trigger.call(this, e);
                }
            });
        });

        if (closeBtn) closeBtn.addEventListener('click', closeModal);
        if (backdrop) backdrop.addEventListener('click', closeModal);
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                closeModal();
            }
        });
    }

    // 9. Floating Back to Top Button
    function initBackToTop() {
        const backToTopBtn = document.getElementById('backToTopBtn');
        if (backToTopBtn) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 400) {
                    backToTopBtn.classList.add('visible');
                } else {
                    backToTopBtn.classList.remove('visible');
                }
            }, { passive: true });

            backToTopBtn.addEventListener('click', () => {
                if (window.tmLenis) window.tmLenis.scrollTo(0, { duration: 1.2 });
                else window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    }

    // Initialize New Interactive Modules
    initLeadershipBioModal();
    initBackToTop();

});

// Site search runs in its own handler so an error in any other module can never disable it.
document.addEventListener('DOMContentLoaded', function () {
    try {
    // Site search — command-palette overlay with live (AJAX) results
    (function initSiteSearch() {
        const root = document.getElementById('siteSearch');
        const trigger = document.getElementById('navSearchOpen');
        if (!root || !trigger) return;
        const input = root.querySelector('#ssInput');
        const form = root.querySelector('.ss-form');
        const resultsEl = root.querySelector('.ss-results');
        const bodyEl = root.querySelector('.ss-body');
        const seeAll = root.querySelector('[data-ss-see-all]');
        const recentWrap = root.querySelector('.ss-recent');
        const recentList = root.querySelector('[data-ss-recent]');
        const suggestUrl = root.dataset.suggestUrl;
        const searchUrl = root.dataset.searchUrl;
        const cache = new Map();
        const RECENT_KEY = 'tm_recent_searches';
        let controller = null;
        let debounceTimer = null;
        let activeIndex = -1;
        let lastFocus = null;

        const isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
        const kbd = document.querySelector('[data-search-kbd]');
        if (kbd) kbd.textContent = isMac ? '⌘ K' : 'Ctrl K';

        const escapeHtml = (str) => String(str || '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
        const escapeRe = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        function highlight(text, query) {
            const safe = escapeHtml(text);
            const terms = query.trim().split(/\s+/).filter((t) => t.length > 1).map(escapeRe);
            if (!terms.length) return safe;
            return safe.replace(new RegExp('(' + terms.join('|') + ')', 'gi'), '<mark>$1</mark>');
        }

        // Recent searches (per-browser convenience; everything works without storage)
        function readRecent() {
            try { return JSON.parse(localStorage.getItem(RECENT_KEY) || '[]').slice(0, 5); } catch (e) { return []; }
        }
        function saveRecent(q) {
            q = q.trim();
            if (q.length < 2) return;
            try { localStorage.setItem(RECENT_KEY, JSON.stringify([q, ...readRecent().filter((r) => r.toLowerCase() !== q.toLowerCase())].slice(0, 5))); } catch (e) { /* storage unavailable */ }
        }
        function renderRecent() {
            const recent = readRecent();
            recentWrap.hidden = !recent.length;
            recentList.innerHTML = recent.map((q) => '<button type="button" class="ss-chip" data-ss-recent-item="' + escapeHtml(q) + '"><i class="fas fa-clock-rotate-left"></i> ' + escapeHtml(q) + '</button>').join('');
        }
        root.querySelector('[data-ss-clear-recent]')?.addEventListener('click', () => {
            try { localStorage.removeItem(RECENT_KEY); } catch (e) { /* ignore */ }
            renderRecent();
            input.focus();
        });
        recentList.addEventListener('click', (e) => {
            const chip = e.target.closest('[data-ss-recent-item]');
            if (!chip) return;
            input.value = chip.dataset.ssRecentItem;
            onInput(true);
            input.focus();
        });

        // Open / close
        function open() {
            if (!root.hidden) return;
            lastFocus = document.activeElement;
            root.hidden = false;
            document.documentElement.classList.add('search-locked');
            window.tmLenis?.stop();
            renderRecent();
            requestAnimationFrame(() => root.classList.add('is-open'));
            setTimeout(() => { input.focus(); input.select(); }, 30);
        }
        function close() {
            if (root.hidden) return;
            root.classList.remove('is-open');
            document.documentElement.classList.remove('search-locked');
            window.tmLenis?.start();
            setTimeout(() => { root.hidden = true; }, 260);
            (lastFocus && lastFocus.focus ? lastFocus : trigger).focus({ preventScroll: true });
        }
        trigger.addEventListener('click', (e) => {
            // The trigger is a real link to /search/ so it still works if this script fails;
            // with JS we open the live overlay instead (modifier-clicks still open a new tab).
            if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
            e.preventDefault();
            open();
        });
        root.querySelectorAll('[data-ss-close]').forEach((el) => el.addEventListener('click', close));
        root.querySelector('.ss-clear').addEventListener('click', () => { input.value = ''; onInput(true); input.focus(); });

        document.addEventListener('keydown', (e) => {
            const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable;
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                root.hidden ? open() : close();
            } else if (e.key === '/' && !typing && root.hidden) {
                e.preventDefault();
                open();
            } else if (e.key === 'Escape' && !root.hidden) {
                e.preventDefault();
                close();
            }
        });

        // Results
        function items() { return Array.from(resultsEl.querySelectorAll('.ss-item')); }
        function setActive(i) {
            const list = items();
            if (!list.length) { activeIndex = -1; input.removeAttribute('aria-activedescendant'); return; }
            activeIndex = (i + list.length) % list.length;
            list.forEach((el, n) => { el.classList.toggle('is-active', n === activeIndex); el.setAttribute('aria-selected', n === activeIndex ? 'true' : 'false'); });
            input.setAttribute('aria-activedescendant', list[activeIndex].id);
            list[activeIndex].scrollIntoView({ block: 'nearest' });
        }

        function render(data, query) {
            seeAll.hidden = false;
            seeAll.href = data.see_all_url;
            seeAll.innerHTML = 'See all results for “' + escapeHtml(query) + '” <i class="fas fa-arrow-right"></i>';
            if (!data.groups.length) {
                resultsEl.innerHTML =
                    '<div class="ss-empty"><div class="ss-empty-icon"><i class="fas fa-magnifying-glass"></i></div>' +
                    '<h6>No results for “' + escapeHtml(query) + '”</h6>' +
                    '<p>Try a different word, like “cloud”, “firewall” or “SharePoint”, or talk to our team directly.</p>' +
                    '<a class="ss-chip" href="/contact/"><i class="fas fa-headset"></i> Contact a solutions expert</a></div>';
                activeIndex = -1;
                return;
            }
            let n = 0;
            resultsEl.innerHTML = data.groups.map((group) =>
                '<div class="ss-group" data-key="' + group.key + '">' +
                    '<div class="ss-group-head"><i class="' + escapeHtml(group.icon) + '"></i>' + escapeHtml(group.label) +
                    '<span class="ss-group-count">' + group.count + '</span></div>' +
                    group.items.map((item) => {
                        const id = 'ss-opt-' + (n++);
                        return '<a class="ss-item" role="option" id="' + id + '" href="' + escapeHtml(item.url) + '" style="animation-delay:' + Math.min(n * 0.025, 0.3) + 's">' +
                            '<span class="ss-item-icon"><i class="' + escapeHtml(item.icon || group.icon) + '"></i></span>' +
                            '<span class="ss-item-body"><span class="ss-item-title">' + highlight(item.title, query) +
                                (item.badge ? ' <span class="ms-badge ms-badge-' + escapeHtml(item.badge.toLowerCase()) + '">' + escapeHtml(item.badge) + '</span>' : '') + '</span>' +
                                (item.subtitle ? '<span class="ss-item-sub">' + highlight(item.subtitle, query) + '</span>' : '') + '</span>' +
                            (item.meta ? '<span class="ss-item-meta">' + escapeHtml(item.meta) + '</span>' : '') +
                            '<i class="fas fa-arrow-right ss-item-go" aria-hidden="true"></i></a>';
                    }).join('') +
                '</div>'
            ).join('');
            setActive(0);
        }

        async function fetchResults(query) {
            if (cache.has(query)) return cache.get(query);
            controller?.abort();
            controller = new AbortController();
            const res = await fetch(suggestUrl + '?q=' + encodeURIComponent(query), { signal: controller.signal, headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            if (!res.ok) throw new Error('Search failed');
            const data = await res.json();
            cache.set(query, data);
            return data;
        }

        function onInput(immediate) {
            const query = input.value.trim();
            root.classList.toggle('has-query', query.length >= 2);
            clearTimeout(debounceTimer);
            if (query.length < 2) {
                controller?.abort();
                root.classList.remove('is-loading');
                resultsEl.innerHTML = '';
                seeAll.hidden = true;
                activeIndex = -1;
                bodyEl.scrollTop = 0;
                return;
            }
            debounceTimer = setTimeout(async () => {
                root.classList.add('is-loading');
                try {
                    const data = await fetchResults(query);
                    if (input.value.trim() === query) { render(data, query); bodyEl.scrollTop = 0; }
                } catch (err) {
                    if (err.name !== 'AbortError') resultsEl.innerHTML = '<div class="ss-empty"><h6>Search is unavailable right now</h6><p>Please press Enter to see full results.</p></div>';
                } finally {
                    if (input.value.trim() === query) root.classList.remove('is-loading');
                }
            }, immediate ? 0 : 160);
        }
        input.addEventListener('input', () => onInput(false));

        input.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') { e.preventDefault(); setActive(activeIndex + 1); }
            else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(activeIndex - 1); }
            else if (e.key === 'Enter') {
                const active = items()[activeIndex];
                saveRecent(input.value);
                if (active) { e.preventDefault(); window.location.href = active.href; }
            }
        });
        resultsEl.addEventListener('mousemove', (e) => {
            const item = e.target.closest('.ss-item');
            if (item) { const i = items().indexOf(item); if (i !== activeIndex) setActive(i); }
        });
        resultsEl.addEventListener('click', (e) => { if (e.target.closest('.ss-item')) saveRecent(input.value); });
        form.addEventListener('submit', (e) => {
            if (input.value.trim().length < 2) { e.preventDefault(); return; }
            saveRecent(input.value);
        });

        // Keep Tab focus inside the dialog
        root.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab') return;
            const focusables = Array.from(root.querySelectorAll('input, button, a[href]')).filter((el) => el.offsetParent !== null);
            const first = focusables[0], last = focusables[focusables.length - 1];
            if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
            else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        });
    })();
    } catch (err) {
        // Leave the trigger as a plain link to /search/ if anything goes wrong.
        if (window.console) console.error('Site search failed to start:', err);
    }
});
