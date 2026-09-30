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

        bar.classList.remove('done');
        bar.style.width = '0%';
        requestAnimationFrame(function () {
            requestAnimationFrame(function () { bar.style.width = '75%'; });
        });
    }, true);
})();

document.addEventListener('DOMContentLoaded', function () {
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

    // 1. Premium Sticky Navbar — scroll state, hide-on-scroll-down, mobile drawer, mega-dropdown
    (function initNavbar() {
        const navbar = document.getElementById('mainNavbar');
        const mobileToggle = document.getElementById('mobileMenuToggle');
        const navContainer = document.getElementById('navbarNavContainer');
        const servicesItem = document.getElementById('servicesNavItem');
        const servicesLink = document.getElementById('servicesNavLink');
        const mobileOverlay = document.querySelector('.mobile-overlay');

        if (!navbar || !mobileToggle || !navContainer) return;

        let lastScrollY = window.scrollY;

        function handleScroll() {
            const currentScrollY = window.scrollY;
            navbar.classList.toggle('scrolled', currentScrollY > 30);

            if (currentScrollY > 160 && currentScrollY > lastScrollY && !navbar.classList.contains('menu-open')) {
                navbar.classList.add('navbar-hidden');
            } else {
                navbar.classList.remove('navbar-hidden');
            }
            lastScrollY = currentScrollY;
        }
        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll();

        function closeMobileMenu() {
            navContainer.classList.remove('mobile-open');
            navbar.classList.remove('menu-open');
            if (mobileOverlay) mobileOverlay.classList.remove('active');
            mobileToggle.setAttribute('aria-expanded', 'false');
            mobileToggle.setAttribute('aria-label', 'Open navigation menu');
            servicesItem?.classList.remove('dropdown-open');
            servicesLink?.setAttribute('aria-expanded', 'false');
        }

        mobileToggle.addEventListener('click', function () {
            const isOpen = navContainer.classList.toggle('mobile-open');
            navbar.classList.toggle('menu-open', isOpen);
            if (mobileOverlay) mobileOverlay.classList.toggle('active', isOpen);
            mobileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            mobileToggle.setAttribute('aria-label', isOpen ? 'Close navigation menu' : 'Open navigation menu');
            navbar.classList.remove('navbar-hidden');
        });

        if (servicesItem && servicesLink) {
            servicesLink.addEventListener('click', function (event) {
                if (window.innerWidth <= 1024) {
                    if (!servicesItem.classList.contains('dropdown-open')) {
                        event.preventDefault();
                        servicesItem.classList.add('dropdown-open');
                        servicesLink.setAttribute('aria-expanded', 'true');
                    }
                }
            });
        }

        navContainer.querySelectorAll('.nav-link:not(#servicesNavLink), .service-menu-link, .view-all-link').forEach(function (link) {
            link.addEventListener('click', function () {
                if (window.innerWidth <= 1024) closeMobileMenu();
            });
        });

        if (mobileOverlay) mobileOverlay.addEventListener('click', closeMobileMenu);

        document.addEventListener('click', function (event) {
            if (window.innerWidth > 1024) return;
            if (!navbar.contains(event.target)) closeMobileMenu();
        });

        window.addEventListener('resize', function () {
            if (window.innerWidth > 1024) closeMobileMenu();
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') closeMobileMenu();
        });

        // Sliding hover indicator behind nav links (desktop only)
        const navList = document.getElementById('navbarNavList');
        const indicator = document.getElementById('navIndicator');
        if (navList && indicator) {
            const links = Array.from(navList.querySelectorAll('.nav-link'));

            function moveIndicatorTo(el) {
                if (!el || window.innerWidth <= 1024) return;
                const listRect = navList.getBoundingClientRect();
                const linkRect = el.getBoundingClientRect();
                indicator.style.width = linkRect.width + 'px';
                indicator.style.transform = 'translateX(' + (linkRect.left - listRect.left) + 'px)';
                indicator.style.opacity = '1';
            }

            links.forEach((link) => {
                link.addEventListener('mouseenter', () => moveIndicatorTo(link));
            });

            navList.addEventListener('mouseleave', () => {
                const activeLink = navList.querySelector('.nav-link.active');
                if (activeLink) {
                    moveIndicatorTo(activeLink);
                    indicator.style.opacity = '0';
                } else {
                    indicator.style.opacity = '0';
                }
            });

            window.addEventListener('resize', () => { indicator.style.opacity = '0'; });
        }

        // Mega-dropdown spotlight: dim sibling categories while one is hovered
        const megaGrid = document.getElementById('megaDropdownGrid');
        if (megaGrid && window.matchMedia('(pointer: fine)').matches) {
            const categories = megaGrid.querySelectorAll('.mega-dropdown-category');
            categories.forEach((cat) => {
                cat.addEventListener('mouseenter', () => megaGrid.classList.add('has-focus'));
            });
            megaGrid.addEventListener('mouseleave', () => megaGrid.classList.remove('has-focus'));
        }
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

    // 4. Accordion Toggle
    document.querySelectorAll('.accordion-header').forEach((header) => {
        header.addEventListener('click', function () {
            const item = this.closest('.accordion-item');
            if (item) item.classList.toggle('open');
        });
    });

    // 5. Mobile Menu Toggle
    const toggle = document.querySelector('.mobile-toggle');
    const nav = document.querySelector('.navbar-nav');
    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
            if (nav.style.display === 'flex') {
                nav.style.flexDirection = 'column';
                nav.style.position = 'absolute';
                nav.style.top = '100%';
                nav.style.left = '0';
                nav.style.right = '0';
                nav.style.background = '#ffffff';
                nav.style.padding = '1.5rem';
                nav.style.boxShadow = '0 10px 25px rgba(0,0,0,0.12)';
            }
        });
    }

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

    // 6b. Scroll Progress Bar
    const scrollProgress = document.querySelector('.scroll-progress');
    if (scrollProgress) {
        const updateScrollProgress = () => {
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = scrollHeight > 0 ? (window.scrollY / scrollHeight) * 100 : 0;
            scrollProgress.style.width = progress + '%';
        };
        window.addEventListener('scroll', updateScrollProgress, { passive: true });
        updateScrollProgress();
    }

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
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    }

    // Initialize New Interactive Modules
    initLeadershipBioModal();
    initBackToTop();

});
