/* FAQs page: instant search with highlighting, accordion, deep links, topic nav, helpful votes. */
(function () {
    'use strict';
    const items = Array.from(document.querySelectorAll('.fq-item'));
    if (!items.length) return;
    const groups = Array.from(document.querySelectorAll('.fq-group'));
    const topics = Array.from(document.querySelectorAll('.fq-topics a'));
    const input = document.getElementById('fqSearch');
    const clearBtn = document.getElementById('fqClear');
    const bar = document.getElementById('fqResultbar');
    const empty = document.getElementById('fqEmpty');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

    const navOffset = () => (document.getElementById('mainNavbar')?.offsetHeight || 76) + 20;
    function scrollToEl(el) {
        const y = el.getBoundingClientRect().top + window.scrollY - navOffset();
        if (window.tmLenis && !reduceMotion) window.tmLenis.scrollTo(y);
        else window.scrollTo({ top: y, behavior: reduceMotion ? 'auto' : 'smooth' });
    }

    // ---- Accordion
    function setOpen(item, open) {
        item.classList.toggle('is-open', open);
        item.querySelector('.fq-q button').setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    items.forEach((item) => {
        item.querySelector('.fq-q button').addEventListener('click', () => {
            const open = !item.classList.contains('is-open');
            setOpen(item, open);
            if (open) history.replaceState(null, '', '#' + item.id);
        });
    });

    function openTarget(id, scroll) {
        const item = document.getElementById(id);
        if (!item || !item.classList.contains('fq-item')) return;
        if (input.value) { input.value = ''; runSearch(); }
        setOpen(item, true);
        item.classList.remove('is-target'); void item.offsetWidth; item.classList.add('is-target');
        if (scroll) setTimeout(() => scrollToEl(item), 60);
    }
    // Popular chips + deep links (#faq-12)
    document.querySelectorAll('[data-open]').forEach((a) => a.addEventListener('click', (e) => {
        e.preventDefault();
        openTarget('faq-' + a.dataset.open, true);
        history.replaceState(null, '', '#faq-' + a.dataset.open);
    }));
    if (/^#faq-\d+$/.test(location.hash)) openTarget(location.hash.slice(1), true);
    else setOpen(items[0], true);
    window.addEventListener('hashchange', () => { if (/^#faq-\d+$/.test(location.hash)) openTarget(location.hash.slice(1), true); });

    // ---- Topic nav: smooth scroll + active state
    topics.forEach((a) => a.addEventListener('click', (e) => {
        const g = document.getElementById(a.getAttribute('href').slice(1));
        if (!g || g.hidden) return;
        e.preventDefault();
        scrollToEl(g);
    }));
    function syncTopic() {
        const y = navOffset() + 60;
        let current = null;
        groups.forEach((g) => { if (!g.hidden && g.getBoundingClientRect().top <= y) current = g; });
        current = current || groups.find((g) => !g.hidden);
        topics.forEach((a) => a.classList.toggle('is-active', current && a.dataset.topic === current.dataset.group));
        const active = topics.find((a) => a.classList.contains('is-active'));
        if (active && window.innerWidth <= 960) {
            const nav = active.parentElement;
            const left = active.offsetLeft - nav.clientWidth / 2 + active.clientWidth / 2;
            if (Math.abs(nav.scrollLeft - left) > 40) nav.scrollTo({ left, behavior: 'smooth' });
        }
    }
    let ticking = false;
    window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { syncTopic(); ticking = false; }); } }, { passive: true });
    syncTopic();

    // ---- Search
    const norm = (s) => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    const escRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    items.forEach((item) => {
        item._q = item.querySelector('.fq-q-text');
        item._a = item.querySelector('.fq-answer');
        item._qHtml = item._q.innerHTML;
        item._aHtml = item._a.innerHTML;
        item._text = norm(item._q.textContent + ' ' + item._a.textContent);
    });
    function highlight(root, words) {
        if (!words.length) return;
        const re = new RegExp('(' + words.map(escRe).join('|') + ')', 'gi');
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        const nodes = [];
        while (walker.nextNode()) nodes.push(walker.currentNode);
        nodes.forEach((n) => {
            if (!re.test(n.nodeValue)) return;
            re.lastIndex = 0;
            const span = document.createElement('span');
            span.innerHTML = n.nodeValue.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])).replace(re, '<mark>$1</mark>');
            n.replaceWith(...span.childNodes);
        });
    }
    function runSearch() {
        const raw = input.value.trim();
        const words = norm(raw).split(/\s+/).filter((w) => w.length > 1);
        clearBtn.hidden = !input.value;
        let shown = 0;
        items.forEach((item) => {
            item._q.innerHTML = item._qHtml;
            item._a.innerHTML = item._aHtml;
            const match = !words.length || words.every((w) => item._text.includes(w));
            item.hidden = !match;
            if (match) shown++;
            if (words.length && match) {
                highlight(item._q, words);
                highlight(item._a, words);
                const inQuestion = words.every((w) => norm(item._q.textContent).includes(w));
                setOpen(item, !inQuestion || shown <= 3);
            }
        });
        groups.forEach((g) => { g.hidden = !g.querySelector('.fq-item:not([hidden])'); });
        topics.forEach((a) => a.classList.toggle('is-empty', !!document.getElementById('topic-' + a.dataset.topic)?.hidden));
        const searching = words.length > 0;
        bar.hidden = !searching || shown === 0;
        empty.hidden = !searching || shown > 0;
        document.getElementById('fqCount').textContent = shown;
        document.getElementById('fqCountText').textContent = (shown === 1 ? 'answer' : 'answers') + ' for “' + raw + '”';
        document.getElementById('fqEmptyQ').textContent = raw;
        if (!searching) items.forEach((item, i) => { if (!location.hash.includes(item.id)) setOpen(item, i === 0 && !location.hash); });
        syncTopic();
    }
    let t = null;
    input.addEventListener('input', () => { clearTimeout(t); t = setTimeout(runSearch, 120); });
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') { input.value = ''; runSearch(); }
        if (e.key === 'Enter') { const first = items.find((i) => !i.hidden); if (first) scrollToEl(first.closest('.fq-group') || first); }
    });
    clearBtn.addEventListener('click', () => { input.value = ''; runSearch(); input.focus(); });
    document.getElementById('fqReset').addEventListener('click', () => { input.value = ''; runSearch(); scrollToEl(document.querySelector('.fq-body')); });
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && !/input|textarea|select/i.test(document.activeElement.tagName)) { e.preventDefault(); input.focus(); }
    });

    // ---- Copy link
    document.querySelectorAll('.fq-copy').forEach((btn) => btn.addEventListener('click', async () => {
        const url = location.origin + location.pathname + '#faq-' + btn.dataset.copy;
        try { await navigator.clipboard.writeText(url); } catch (e) { window.prompt('Copy this link', url); return; }
        btn.classList.add('is-done');
        btn.querySelector('span').textContent = 'Link copied';
        setTimeout(() => { btn.classList.remove('is-done'); btn.querySelector('span').textContent = 'Copy link'; }, 2000);
    }));

    // ---- Helpful votes
    document.querySelectorAll('.fq-vote').forEach((box) => box.addEventListener('click', async (e) => {
        const btn = e.target.closest('button[data-answer]');
        if (!btn || box.classList.contains('is-voted')) return;
        btn.classList.add('is-picked');
        box.classList.add('is-voted');
        try {
            await fetch(box.dataset.url, { method: 'POST', headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' }, body: 'answer=' + btn.dataset.answer });
        } catch (err) { /* the vote is a nicety; the UI already thanked them */ }
    }));
})();
