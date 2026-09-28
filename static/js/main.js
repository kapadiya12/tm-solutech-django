document.addEventListener('DOMContentLoaded', function () {
    // 1. Animated Sticky Glassmorphism Navbar
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const updateNavbar = () => {
            if (window.scrollY > 40) {
                navbar.classList.add('scrolled');
                navbar.classList.remove('transparent');
            } else {
                navbar.classList.remove('scrolled');
                if (navbar.getAttribute('data-transparent') === 'true') {
                    navbar.classList.add('transparent');
                }
            }
        };
        updateNavbar();
        window.addEventListener('scroll', updateNavbar, { passive: true });
    }

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
            const body = this.nextElementSibling;
            if (body && body.classList.contains('accordion-body')) {
                const isOpen = body.style.display === 'block' || getComputedStyle(body).display === 'block';
                body.style.display = isOpen ? 'none' : 'block';
            }
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

    // 6. Auto-dismiss Toasts
    document.querySelectorAll('.toast').forEach((toast) => {
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    });

    // 7. Leadership / Director Interactive Carousel
    function initLeadershipCarousel() {
        const track = document.getElementById('leadershipCarouselTrack');
        const viewport = document.getElementById('leadershipCarouselViewport');
        const prevBtn = document.getElementById('leaderPrevBtn');
        const nextBtn = document.getElementById('leaderNextBtn');
        const counterEl = document.getElementById('leaderCounter');
        const dotsContainer = document.getElementById('leadershipDots');
        if (!track || !viewport) return;

        const slides = Array.from(track.querySelectorAll('.leadership-slide'));
        if (slides.length === 0) return;

        let currentIndex = 0;
        let autoSlideInterval = null;
        let startX = 0;
        let isDragging = false;

        function getVisibleCount() {
            if (window.innerWidth <= 640) return 1;
            if (window.innerWidth <= 1024) return 2;
            return 3;
        }

        function getMaxIndex() {
            const visible = getVisibleCount();
            return Math.max(0, slides.length - visible);
        }

        function updateDots() {
            if (!dotsContainer) return;
            dotsContainer.innerHTML = '';
            const maxIdx = getMaxIndex();
            for (let i = 0; i <= maxIdx; i++) {
                const dot = document.createElement('button');
                dot.className = 'leader-dot' + (i === currentIndex ? ' active' : '');
                dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
                dot.addEventListener('click', () => {
                    goToSlide(i);
                    resetAutoSlide();
                });
                dotsContainer.appendChild(dot);
            }
        }

        function updateCarousel() {
            const maxIdx = getMaxIndex();
            if (currentIndex > maxIdx) currentIndex = maxIdx;
            if (currentIndex < 0) currentIndex = 0;

            const slideWidth = slides[0].getBoundingClientRect().width;
            const gap = 28; // 1.75rem
            const offset = currentIndex * (slideWidth + gap);

            track.style.transform = `translateX(-${offset}px)`;

            if (counterEl) {
                counterEl.textContent = `${currentIndex + 1} / ${maxIdx + 1}`;
            }

            if (prevBtn) prevBtn.style.opacity = currentIndex === 0 ? '0.5' : '1';
            if (nextBtn) nextBtn.style.opacity = currentIndex >= maxIdx ? '0.5' : '1';

            if (dotsContainer) {
                const dots = dotsContainer.querySelectorAll('.leader-dot');
                dots.forEach((dot, idx) => {
                    dot.classList.toggle('active', idx === currentIndex);
                });
            }
        }

        function goToSlide(index) {
            currentIndex = index;
            updateCarousel();
        }

        function nextSlide() {
            const maxIdx = getMaxIndex();
            if (currentIndex >= maxIdx) {
                currentIndex = 0;
            } else {
                currentIndex++;
            }
            updateCarousel();
        }

        function prevSlide() {
            const maxIdx = getMaxIndex();
            if (currentIndex <= 0) {
                currentIndex = maxIdx;
            } else {
                currentIndex--;
            }
            updateCarousel();
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                nextSlide();
                resetAutoSlide();
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                prevSlide();
                resetAutoSlide();
            });
        }

        function startAutoSlide() {
            stopAutoSlide();
            autoSlideInterval = setInterval(nextSlide, 5000);
        }

        function stopAutoSlide() {
            if (autoSlideInterval) clearInterval(autoSlideInterval);
        }

        function resetAutoSlide() {
            stopAutoSlide();
            startAutoSlide();
        }

        viewport.addEventListener('mouseenter', stopAutoSlide);
        viewport.addEventListener('mouseleave', startAutoSlide);

        // Touch & Drag Support
        viewport.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            stopAutoSlide();
        }, { passive: true });

        viewport.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const diff = endX - startX;
            if (diff > 45) {
                prevSlide();
            } else if (diff < -45) {
                nextSlide();
            }
            startAutoSlide();
        }, { passive: true });

        viewport.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            stopAutoSlide();
        });

        window.addEventListener('mouseup', (e) => {
            if (!isDragging) return;
            isDragging = false;
            const diff = e.clientX - startX;
            if (diff > 50) {
                prevSlide();
            } else if (diff < -50) {
                nextSlide();
            }
            startAutoSlide();
        });

        window.addEventListener('resize', () => {
            updateDots();
            updateCarousel();
        });

        updateDots();
        updateCarousel();
        startAutoSlide();
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
            btn.addEventListener('click', function (e) {
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
    initLeadershipCarousel();
    initLeadershipBioModal();
    initBackToTop();

});
