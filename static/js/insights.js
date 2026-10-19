/* Insights: AJAX search + filters + load more (listing), reading progress,
   table of contents, share, helpful vote (article). */
(function () {
    'use strict';
    const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const toast = document.getElementById('insToast');
    let toastTimer = null;
    function flash(html) {
        if (!toast) return;
        toast.innerHTML = html; toast.hidden = false;
        requestAnimationFrame(() => toast.classList.add('is-on'));
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => { toast.classList.remove('is-on'); setTimeout(() => { toast.hidden = true; }, 300); }, 1800);
    }

    /* =================================================================
       LISTING
       ================================================================= */
    const form = document.getElementById('insSearch');
    if (form) {
        const endpoint = form.dataset.endpoint;
        const input = document.getElementById('insQ');
        const clearBtn = document.getElementById('insClear');
        const suggest = document.getElementById('insSuggest');
        const grid = document.getElementById('insGrid');
        const empty = document.getElementById('insEmpty');
        const more = document.getElementById('insMore');
        const featured = document.getElementById('insTop');
        const heading = document.getElementById('insHeading');
        const result = document.getElementById('insResult');
        const countEl = document.getElementById('insCount');
        const sort = document.getElementById('insSort');
        const chips = Array.from(document.querySelectorAll('.ins-chip-btn'));
        const params = new URLSearchParams(location.search);
        const state = { q: params.get('q') || '', category: params.get('category') || '', sort: params.get('sort') || 'latest', tag: params.get('tag') || '' };
        let controller = null;
        let activeIdx = -1;
        let lastSuggest = [];

        const qs = (extra) => {
            const p = new URLSearchParams();
            Object.entries(Object.assign({}, state, extra || {})).forEach(([k, v]) => { if (v && !(k === 'sort' && v === 'latest')) p.set(k, v); });
            return p.toString();
        };
        const syncUrl = () => {
            const s = qs();
            history.replaceState(null, '', location.pathname + (s ? '?' + s : ''));
        };

        async function load(page, append) {
            if (controller) controller.abort();
            controller = new AbortController();
            form.classList.add('is-loading');
            if (!append) grid.classList.add('is-swapping');
            try {
                const res = await fetch(endpoint + '?' + qs({ page: page || 1 }), { signal: controller.signal, headers: { 'X-Requested-With': 'fetch' } });
                const data = await res.json();
                if (append) grid.insertAdjacentHTML('beforeend', data.html);
                else grid.innerHTML = data.html;
                const filtering = !!(state.q || state.category || state.tag);
                if (featured) featured.hidden = !data.featured;
                const topic = state.category && !state.q && !state.tag ? chips.find((c) => c.dataset.category === state.category) : null;
                if (heading) heading.textContent = topic ? topic.dataset.name : filtering ? 'Results' : (state.sort === 'popular' ? 'Most read articles' : state.sort === 'oldest' ? 'Oldest articles' : 'Latest articles');
                const intro = document.getElementById('insIntro');
                if (intro) { intro.textContent = topic ? topic.dataset.desc || '' : ''; intro.hidden = !intro.textContent; }
                // the featured post is excluded server-side only on the initial render; re-show it inside the grid when filtering
                empty.hidden = data.count > 0;
                more.hidden = !data.has_next;
                more.dataset.next = data.has_next ? data.page + 1 : '';
                result.hidden = !filtering;
                countEl.textContent = data.count;
                document.getElementById('insResultText').textContent = ' result' + (data.count === 1 ? '' : 's') + (state.tag ? ' tagged “' + state.tag + '”' : '') + (state.q ? ' for “' + state.q + '”' : '');
                renderSuggest(data.suggestions || []);
                syncUrl();
            } catch (e) {
                if (e.name !== 'AbortError') flash('<i class="fas fa-circle-exclamation"></i> Could not load articles');
            } finally {
                form.classList.remove('is-loading');
                grid.classList.remove('is-swapping');
                more.classList.remove('is-loading');
            }
        }

        function highlight(text, q) {
            const out = esc(text);
            if (!q) return out;
            const words = q.split(/\s+/).filter((w) => w.length > 1).map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
            return words.length ? out.replace(new RegExp('(' + words.join('|') + ')', 'gi'), '<mark>$1</mark>') : out;
        }
        const defaultTpl = document.getElementById('insSuggestDefault');
        function renderDefault() {
            if (!defaultTpl || document.activeElement !== input) return;
            suggest.innerHTML = defaultTpl.innerHTML;
            lastSuggest = Array.from(suggest.querySelectorAll('a[data-i]')).map((a) => ({ url: a.getAttribute('href') }));
            activeIdx = -1;
            suggest.classList.add('is-default');
            suggest.hidden = !suggest.innerHTML.trim();
        }
        function renderSuggest(items) {
            lastSuggest = items;
            activeIdx = -1;
            suggest.classList.remove('is-default');
            if (!state.q) { renderDefault(); return; }
            if (document.activeElement !== input) { suggest.hidden = true; return; }
            if (!items.length) {
                suggest.innerHTML = '<div class="ins-suggest-empty">No articles match “' + esc(state.q) + '”.</div>';
            } else {
                suggest.innerHTML = items.map((it, i) =>
                    '<a href="' + it.url + '" role="option" data-i="' + i + '"><i class="fas fa-file-lines"></i><span><strong>' + highlight(it.title, state.q) + '</strong><small>' + esc(it.category || 'Insights') + ' · ' + it.minutes + ' min read</small></span></a>'
                ).join('') + '<a class="ins-suggest-all" href="#" data-all>See all results <i class="fas fa-arrow-down"></i></a>';
            }
            suggest.hidden = false;
        }
        function setActive(i) {
            const links = Array.from(suggest.querySelectorAll('a[data-i]'));
            if (!links.length) return;
            activeIdx = (i + links.length) % links.length;
            links.forEach((a, k) => a.classList.toggle('is-active', k === activeIdx));
        }

        let typing = null;
        input.addEventListener('input', () => {
            state.q = input.value.trim();
            clearBtn.hidden = !input.value;
            clearTimeout(typing);
            typing = setTimeout(() => load(1, false), 260);
        });
        input.addEventListener('keydown', (e) => {
            if (suggest.hidden) return;
            if (e.key === 'ArrowDown') { e.preventDefault(); setActive(activeIdx + 1); }
            else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(activeIdx - 1); }
            else if (e.key === 'Enter' && activeIdx >= 0 && lastSuggest[activeIdx]) { e.preventDefault(); location.href = lastSuggest[activeIdx].url; }
            else if (e.key === 'Escape') { suggest.hidden = true; }
        });
        input.addEventListener('focus', () => { if (state.q && lastSuggest) renderSuggest(lastSuggest); else if (!state.q) renderDefault(); });
        input.addEventListener('click', () => { if (!state.q && suggest.hidden) renderDefault(); });
        document.addEventListener('click', (e) => { if (!form.contains(e.target)) suggest.hidden = true; });
        suggest.addEventListener('mousedown', (e) => { if (e.target.closest('button')) e.preventDefault(); });   // keep focus in the input
        suggest.addEventListener('click', (e) => {
            const term = e.target.closest('[data-term]');
            if (term) { input.value = term.dataset.term; state.q = input.value; clearBtn.hidden = false; load(1, false); return; }
            const topic = e.target.closest('[data-topic]');
            if (topic) {
                suggest.hidden = true;
                chips.find((c) => c.dataset.category === topic.dataset.topic)?.click();
                grid.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
                return;
            }
            if (e.target.closest('[data-all]')) { e.preventDefault(); suggest.hidden = true; grid.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' }); }
        });
        form.addEventListener('submit', (e) => { e.preventDefault(); suggest.hidden = true; load(1, false); grid.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' }); });
        clearBtn.addEventListener('click', () => {
            if (!input.value) { suggest.hidden = true; input.blur(); return; }   // nothing typed: just close the panel
            input.value = ''; state.q = ''; input.focus(); renderDefault(); load(1, false);
        });
        // The cross shows while there's text or the suggestions are open
        const syncClear = () => { clearBtn.hidden = !input.value && suggest.hidden; clearBtn.setAttribute('aria-label', input.value ? 'Clear search' : 'Close suggestions'); };
        new MutationObserver(syncClear).observe(suggest, { attributes: true, attributeFilter: ['hidden'] });
        input.addEventListener('input', syncClear);

        // "/" focuses search
        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && !/input|textarea|select/i.test(document.activeElement.tagName)) { e.preventDefault(); input.focus(); }
        });

        chips.forEach((chip) => chip.addEventListener('click', () => {
            chips.forEach((c) => c.classList.toggle('is-active', c === chip));
            state.category = chip.dataset.category;
            state.tag = '';
            load(1, false);
        }));
        sort.addEventListener('change', () => { state.sort = sort.value; load(1, false); });

        // Styled sort dropdown
        const sBtn = document.getElementById('insSortBtn');
        const sMenu = document.getElementById('insSortMenu');
        const sLabel = document.getElementById('insSortLabel');
        if (sBtn && sMenu) {
            const opts = Array.from(sMenu.querySelectorAll('[data-value]'));
            let sIdx = -1;
            const open = (on) => {
                sMenu.hidden = !on; sBtn.setAttribute('aria-expanded', on ? 'true' : 'false');
                sBtn.classList.toggle('is-open', on);
                if (on) { sIdx = opts.findIndex((o) => o.dataset.value === sort.value); mark(); }
            };
            const mark = () => opts.forEach((o, i) => o.classList.toggle('is-active', i === sIdx));
            const pick = (o) => {
                opts.forEach((x) => x.setAttribute('aria-selected', x === o ? 'true' : 'false'));
                sLabel.textContent = o.textContent.trim();
                open(false); sBtn.focus();
                if (sort.value !== o.dataset.value) { sort.value = o.dataset.value; sort.dispatchEvent(new Event('change')); }
            };
            sBtn.addEventListener('click', () => open(sMenu.hidden));
            opts.forEach((o) => o.addEventListener('click', () => pick(o)));
            sBtn.addEventListener('keydown', (e) => {
                if (['ArrowDown', 'ArrowUp'].includes(e.key)) { e.preventDefault(); if (sMenu.hidden) open(true); else { sIdx = (sIdx + (e.key === 'ArrowDown' ? 1 : -1) + opts.length) % opts.length; mark(); } }
                else if (e.key === 'Enter' && !sMenu.hidden && opts[sIdx]) { e.preventDefault(); pick(opts[sIdx]); }
                else if (e.key === 'Escape') open(false);
            });
            document.addEventListener('click', (e) => { if (!e.target.closest('#insSortWrap')) open(false); });
        }
        more.addEventListener('click', () => {
            if (!more.dataset.next) return;
            more.classList.add('is-loading');
            load(Number(more.dataset.next), true);
        });
        const reset = () => {
            state.q = ''; state.category = ''; state.tag = ''; state.sort = 'latest';
            input.value = ''; clearBtn.hidden = true; sort.value = 'latest';
            const lab = document.getElementById('insSortLabel'); if (lab) lab.textContent = 'Latest';
            document.querySelectorAll('#insSortMenu [data-value]').forEach((o) => o.setAttribute('aria-selected', o.dataset.value === 'latest' ? 'true' : 'false'));
            chips.forEach((c) => c.classList.toggle('is-active', !c.dataset.category));
            load(1, false);
        };
        document.getElementById('insReset')?.addEventListener('click', reset);
        document.querySelectorAll('[data-reset]').forEach((b) => b.addEventListener('click', reset));
    }

    /* =================================================================
       ARTICLE
       ================================================================= */
    const article = document.getElementById('insArticle');
    if (!article) return;

    // Reading progress (one write per frame)
    const bar = document.getElementById('insProgress');
    if (bar) {
        let ticking = false;
        const update = () => {
            const r = article.getBoundingClientRect();
            const total = r.height - window.innerHeight * 0.6;
            const done = Math.min(Math.max(-r.top + window.innerHeight * 0.2, 0), Math.max(total, 1));
            bar.style.transform = 'scaleX(' + (done / Math.max(total, 1)).toFixed(4) + ')';
            ticking = false;
        };
        window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
        update();
    }

    // Table of contents from h2/h3
    const toc = document.getElementById('insToc');
    const list = document.getElementById('insTocList');
    const heads = Array.from(article.querySelectorAll('h2, h3')).filter((h) => !h.closest('.ins-helpful, .ins-author-box'));
    if (toc && heads.length >= 2) {
        const slug = (t) => t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) || 'section';
        const used = {};
        heads.forEach((h) => {
            let id = h.id || slug(h.textContent);
            while (used[id]) id += '-2';
            used[id] = 1; h.id = id;
            const li = document.createElement('li');
            if (h.tagName === 'H3') li.className = 'is-sub';
            li.innerHTML = '<a href="#' + id + '">' + esc(h.textContent.trim()) + '</a>';
            list.appendChild(li);
        });
        toc.hidden = false;
        const links = Array.from(list.querySelectorAll('a'));
        if ('IntersectionObserver' in window) {
            const visible = new Set();
            const spy = new IntersectionObserver((entries) => {
                entries.forEach((e) => (e.isIntersecting ? visible.add(e.target) : visible.delete(e.target)));
                const first = heads.find((h) => visible.has(h));
                if (first) links.forEach((a) => a.classList.toggle('is-active', a.hash === '#' + first.id));
            }, { rootMargin: '-15% 0px -70% 0px' });
            heads.forEach((h) => spy.observe(h));
        }
    }

    // Copy link
    document.querySelectorAll('[data-copy-link]').forEach((b) => b.addEventListener('click', async () => {
        try { await navigator.clipboard.writeText(location.href.split('#')[0]); flash('<i class="fas fa-circle-check"></i> Link copied'); }
        catch (e) { flash('Press Ctrl+C to copy the address'); }
    }));

    // Helpful vote
    const helpful = document.getElementById('insHelpful');
    if (helpful) {
        const thanks = helpful.querySelector('.ins-helpful-thanks');
        const done = () => { helpful.classList.add('is-voted'); thanks.hidden = false; };
        if (helpful.dataset.voted) done();
        helpful.querySelectorAll('[data-answer]').forEach((btn) => btn.addEventListener('click', async () => {
            const body = new FormData();
            body.append('answer', btn.dataset.answer);
            const token = (helpful.querySelector('input[name=csrfmiddlewaretoken]') || {}).value || (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
            try {
                const res = await fetch(helpful.dataset.url, { method: 'POST', body, headers: { 'X-CSRFToken': token, 'X-Requested-With': 'fetch' }, credentials: 'same-origin' });
                if (res.ok) done(); else flash('Could not save your vote');
            } catch (e) { flash('Could not save your vote'); }
        }));
    }
})();
