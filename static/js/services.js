/* Services pages: carousels, scroll reveal, sticky section nav, timeline, spotlight, tilt, accordion. */
(function () {
    'use strict';
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const navH = () => (document.getElementById('mainNavbar')?.offsetHeight || 72);

    function smoothTo(el, extra) {
        const y = el.getBoundingClientRect().top + window.scrollY - navH() - (extra || 0);
        if (window.tmLenis && !reduceMotion) window.tmLenis.scrollTo(y);
        else window.scrollTo({ top: y, behavior: reduceMotion ? 'auto' : 'smooth' });
    }

    // The sticky section bar sits just under the navbar (and moves to the top when the navbar tucks away)
    const setNavOffset = () => document.documentElement.style.setProperty('--sv-nav-offset', navH() + 'px');
    setNavOffset();
    window.addEventListener('resize', setNavOffset);

    /* ---------- Reveal on scroll ---------- */
    const revealIO = 'IntersectionObserver' in window ? new IntersectionObserver((entries) => {
        entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); revealIO.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 }) : null;
    document.querySelectorAll('[data-reveal], [data-timeline]').forEach((el) => {
        if (revealIO && !reduceMotion) revealIO.observe(el); else el.classList.add('is-in');
    });

    /* ---------- In-page anchor links ---------- */
    document.querySelectorAll('a[data-scroll], .sv-subnav-links a').forEach((a) => a.addEventListener('click', (e) => {
        const id = a.getAttribute('href');
        if (!id || id.charAt(0) !== '#') return;
        const target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        smoothTo(target, document.querySelector('[data-subnav]') ? 64 : 12);
        history.replaceState(null, '', id);
    }));

    /* ---------- Sticky section nav: scroll spy + reading progress ---------- */
    const subnav = document.querySelector('[data-subnav]');
    if (subnav) {
        const links = Array.from(subnav.querySelectorAll('.sv-subnav-links a'));
        const sections = links.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);
        const bar = subnav.querySelector('[data-subnav-progress]');
        const main = document.querySelector('.sv-overview');
        let ticking = false;
        const update = () => {
            ticking = false;
            const line = navH() + 90;
            let current = sections[0];
            sections.forEach((s) => { if (s.getBoundingClientRect().top <= line) current = s; });
            links.forEach((a) => a.classList.toggle('is-active', current && a.getAttribute('href') === '#' + current.id));
            const active = links.find((a) => a.classList.contains('is-active'));
            if (active) {
                const wrap = active.parentElement;
                const left = active.offsetLeft - wrap.clientWidth / 2 + active.clientWidth / 2;
                if (Math.abs(wrap.scrollLeft - left) > 30) wrap.scrollTo({ left, behavior: 'smooth' });
            }
            if (bar && main) {
                const start = main.offsetTop - navH();
                const end = document.documentElement.scrollHeight - window.innerHeight;
                bar.style.setProperty('--p', Math.min(1, Math.max(0, (window.scrollY - start) / Math.max(1, end - start))));
            }
        };
        window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
        update();
    }

    /* ---------- Carousels: auto-advance one card every 5s, dots, swipe; no arrows ---------- */
    document.querySelectorAll('[data-carousel]').forEach((root) => {
        const track = root.querySelector('[data-track]');
        if (!track) return;
        root.querySelectorAll('.sv-progress, .sv-arrows').forEach((el) => el.remove());
        const slides = Array.from(track.children);
        const perView = () => {
            const w = window.innerWidth;
            const cols = track.classList.contains('sv-track-2') ? (w > 1024 ? 3 : w > 760 ? 2 : 1) : (w > 1200 ? 4 : w > 1024 ? 3 : w > 760 ? 2 : 1);
            return cols;
        };
        if (slides.length <= 1) return;
        const viewport = document.createElement('div');
        viewport.className = 'sv-cviewport';
        const rail = document.createElement('div');
        rail.className = 'sv-crail';
        slides.forEach((el) => rail.appendChild(el));
        // clones at the end for a seamless wrap
        slides.forEach((el) => {
            const c = el.cloneNode(true);
            c.setAttribute('aria-hidden', 'true');
            c.setAttribute('tabindex', '-1');
            c.querySelectorAll('a,button').forEach((x) => x.setAttribute('tabindex', '-1'));
            rail.appendChild(c);
        });
        viewport.appendChild(rail);
        track.replaceWith(viewport);
        const dots = document.createElement('div');
        dots.className = 'sv-dots';
        dots.setAttribute('role', 'tablist');
        slides.forEach((_, i) => {
            const d = document.createElement('button');
            d.type = 'button'; d.setAttribute('aria-label', 'Show item ' + (i + 1));
            d.addEventListener('click', () => { go(i); restart(); });
            dots.appendChild(d);
        });
        viewport.after(dots);

        let index = 0, timer = null, hover = false, visible = false;
        const n = slides.length;
        const layout = () => {
            const pv = Math.min(perView(), n);
            root.style.setProperty('--pv', pv);
            const static_ = n <= pv;
            root.classList.toggle('is-static', static_);
            dots.hidden = static_;
            return static_;
        };
        const stepPx = () => {
            const a = rail.children[0].getBoundingClientRect(), b = rail.children[1].getBoundingClientRect();
            return b.left - a.left;
        };
        const paint = (animate) => {
            rail.style.transition = animate === false ? 'none' : '';
            rail.style.transform = `translate3d(${-index * stepPx()}px,0,0)`;
            Array.from(dots.children).forEach((d, i) => d.classList.toggle('is-active', i === index % n));
        };
        function go(i) {
            index = i;
            paint();
        }
        rail.addEventListener('transitionend', () => {
            if (index >= n) { index -= n; paint(false); }   // jumped into the clones: snap back invisibly
        });
        const next = () => { if (index >= n) { index -= n; paint(false); void rail.offsetWidth; } go(index + 1); };
        const prev = () => { if (index <= 0) { index += n; paint(false); void rail.offsetWidth; } go(index - 1); };
        function restart() {
            clearInterval(timer);
            if (reduceMotion || root.classList.contains('is-static')) return;
            timer = setInterval(() => { if (visible && !hover && !document.hidden) next(); }, 5000);
        }
        root.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') hover = true; });
        root.addEventListener('pointerleave', () => { hover = false; });
        root.addEventListener('focusin', () => { hover = true; });
        root.addEventListener('focusout', () => { hover = false; });
        if ('IntersectionObserver' in window) new IntersectionObserver((es) => { visible = es[0].isIntersecting; }, { threshold: 0.3 }).observe(root);
        else visible = true;
        // swipe / drag
        let x0 = null, moved = false;
        viewport.addEventListener('pointerdown', (e) => { x0 = e.clientX; moved = false; });
        viewport.addEventListener('pointerup', (e) => {
            if (x0 === null) return;
            const dx = e.clientX - x0; x0 = null;
            if (Math.abs(dx) > 40) { moved = true; (dx < 0 ? next : prev)(); restart(); }
        });
        viewport.addEventListener('click', (e) => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
        let rt = null;
        window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { layout(); paint(false); restart(); }, 150); });
        layout(); paint(false); restart();
    });

    /* ---------- Spotlight: cursor-following glow on cards ---------- */
    if (window.matchMedia('(hover: hover)').matches) {
        document.addEventListener('pointermove', (e) => {
            const card = e.target.closest && e.target.closest('[data-spotlight]');
            if (!card) return;
            const r = card.getBoundingClientRect();
            card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
            card.style.setProperty('--my', (e.clientY - r.top) + 'px');
        }, { passive: true });
    }

    /* ---------- Hero image tilt ---------- */
    const tilt = document.querySelector('[data-tilt]');
    if (tilt && !reduceMotion && window.matchMedia('(hover: hover) and (min-width: 761px)').matches) {
        const frame = tilt.querySelector('.sv-hero-frame');
        tilt.addEventListener('pointermove', (e) => {
            const r = tilt.getBoundingClientRect();
            const px = (e.clientX - r.left) / r.width - 0.5;
            const py = (e.clientY - r.top) / r.height - 0.5;
            frame.style.setProperty('--ry', (px * 10).toFixed(2) + 'deg');
            frame.style.setProperty('--rx', (-py * 8).toFixed(2) + 'deg');
        });
        tilt.addEventListener('pointerleave', () => { frame.style.removeProperty('--ry'); frame.style.removeProperty('--rx'); });
    }

    /* ---------- Accordion ---------- */
    document.querySelectorAll('[data-accordion]').forEach((acc) => {
        acc.querySelectorAll('.sv-acc-q').forEach((btn) => btn.addEventListener('click', () => {
            const item = btn.closest('.sv-acc-item');
            const open = !item.classList.contains('is-open');
            acc.querySelectorAll('.sv-acc-item.is-open').forEach((o) => { o.classList.remove('is-open'); o.querySelector('.sv-acc-q').setAttribute('aria-expanded', 'false'); });
            item.classList.toggle('is-open', open);
            btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        }));
    });
})();
