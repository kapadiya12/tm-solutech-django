/* Tima: TM Solutech AI assistant widget */
(function () {
    'use strict';
    const root = document.getElementById('tmAi');
    if (!root) return;
    const $ = (id) => document.getElementById(id);
    const panel = $('tmAiPanel'), launcher = $('tmAiLauncher'), body = $('tmAiBody'), form = $('tmAiForm'), input = $('tmAiInput');
    const nudge = $('tmAiNudge');
    const endpoint = root.dataset.endpoint;
    const csrf = root.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    const STORE = 'tmAi.v1';
    const THINKING = ['Thinking', 'Checking our services', 'Putting it together'];
    let state = load();
    let busy = false;

    function load() {
        try { return JSON.parse(sessionStorage.getItem(STORE)) || { token: '', turns: [] }; } catch (e) { return { token: '', turns: [] }; }
    }
    function save() { try { sessionStorage.setItem(STORE, JSON.stringify(state)); } catch (e) { /* private mode */ } }

    /* Safe mini-markdown: escape first, then bold, links (site paths only), lists, paragraphs */
    function esc(s) { return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
    function inline(s) {
        return s
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\[([^\]]+)\]\((\/[^)\s]*|mailto:[^)\s]+|tel:[^)\s]+)\)/g, '<a href="$2">$1</a>');
    }
    function md(text) {
        const lines = esc(text).split('\n');
        let html = '', list = null;
        const close = () => { if (list) { html += `</${list}>`; list = null; } };
        lines.forEach((raw) => {
            const line = raw.trim();
            const ul = line.match(/^[-*•]\s+(.*)/), ol = line.match(/^\d+[.)]\s+(.*)/);
            if (ul || ol) {
                const tag = ul ? 'ul' : 'ol';
                if (list !== tag) { close(); html += `<${tag}>`; list = tag; }
                html += `<li>${inline((ul || ol)[1])}</li>`;
            } else if (!line) {
                close();
            } else {
                close();
                html += `<p>${inline(line)}</p>`;
            }
        });
        close();
        return html;
    }

    function scrollDown() { body.scrollTop = body.scrollHeight; }
    function addMsg(role, text, opts) {
        const wrap = document.createElement('div');
        wrap.className = 'tm-ai-msg ' + (role === 'user' ? 'tm-ai-user' : 'tm-ai-bot');
        const bubble = document.createElement('div');
        bubble.className = 'tm-ai-bubble';
        if (role === 'user') bubble.textContent = text; else bubble.innerHTML = md(text);
        wrap.appendChild(bubble);
        body.appendChild(wrap);
        if (opts && opts.lead) {
            const note = document.createElement('div');
            note.className = 'tm-ai-lead';
            note.innerHTML = '<i class="fas fa-circle-check"></i> Your details were shared with our team.';
            body.appendChild(note);
        }
        scrollDown();
        return wrap;
    }
    function addChips(list) {
        body.querySelectorAll('.tm-ai-chips.is-follow').forEach((c) => c.remove());
        if (!list || !list.length) return;
        const box = document.createElement('div');
        box.className = 'tm-ai-chips is-follow';
        list.forEach((q) => {
            const b = document.createElement('button');
            b.type = 'button'; b.className = 'tm-ai-chip'; b.dataset.q = q; b.textContent = q;
            box.appendChild(b);
        });
        body.appendChild(box);
        scrollDown();
    }
    function typing() {
        const wrap = document.createElement('div');
        wrap.className = 'tm-ai-msg tm-ai-bot';
        wrap.innerHTML = '<div class="tm-ai-bubble"><span class="tm-ai-typing"><span class="tm-ai-dots"><i></i><i></i><i></i></span><small></small></span></div>';
        body.appendChild(wrap);
        const label = wrap.querySelector('small');
        let i = 0; label.textContent = THINKING[0] + '…';
        const t = setInterval(() => { i = (i + 1) % THINKING.length; label.textContent = THINKING[i] + '…'; }, 1600);
        scrollDown();
        return () => { clearInterval(t); wrap.remove(); };
    }

    // Typewriter reveal for the reply (fast, cancels on long text)
    function reveal(el, text) {
        return new Promise((resolve) => {
            const bubble = el.querySelector('.tm-ai-bubble');
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || text.length > 900) { bubble.innerHTML = md(text); resolve(); return; }
            let n = 0;
            const step = Math.max(2, Math.round(text.length / 90));
            const tick = () => {
                n = Math.min(text.length, n + step);
                bubble.innerHTML = md(text.slice(0, n));
                scrollDown();
                if (n < text.length) requestAnimationFrame(tick); else resolve();
            };
            tick();
        });
    }

    async function send(text) {
        text = text.trim();
        if (!text || busy) return;
        busy = true;
        form.querySelector('.tm-ai-send').disabled = true;
        $('tmAiStart')?.remove();
        body.querySelectorAll('.tm-ai-chips.is-follow').forEach((c) => c.remove());
        addMsg('user', text);
        state.turns.push({ role: 'user', text });
        save();
        input.value = ''; autosize();
        root.classList.add('is-thinking');
        const stop = typing();
        let data;
        try {
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
                body: JSON.stringify({ message: text, token: state.token, page: location.pathname }),
            });
            data = await res.json();
        } catch (e) {
            data = { reply: 'I lost my connection for a moment. Please try again.', suggestions: [] };
        }
        stop();
        root.classList.remove('is-thinking');
        if (data.token) state.token = data.token;
        const reply = data.reply || 'Sorry, something went wrong. Please try again.';
        const el = addMsg('bot', '');
        root.classList.add('is-talking');
        await reveal(el, reply);
        root.classList.remove('is-talking');
        if (data.lead) {
            const note = document.createElement('div');
            note.className = 'tm-ai-lead';
            note.innerHTML = '<i class="fas fa-circle-check"></i> Your details were shared with our team.';
            body.appendChild(note);
            root.classList.add('is-happy'); setTimeout(() => root.classList.remove('is-happy'), 900);
        }
        state.turns.push({ role: 'bot', text: reply, lead: !!data.lead });
        state.suggestions = data.suggestions || [];
        save();
        addChips(state.suggestions);
        busy = false;
        form.querySelector('.tm-ai-send').disabled = false;
        input.focus({ preventScroll: true });
    }

    function open() {
        panel.hidden = false;
        root.classList.add('is-open');
        launcher.setAttribute('aria-expanded', 'true');
        if (nudge) nudge.hidden = true;
        try { localStorage.setItem('tmAi.nudged', '1'); } catch (e) { /* ignore */ }
        scrollDown();
        if (window.matchMedia('(min-width: 641px)').matches) setTimeout(() => input.focus({ preventScroll: true }), 120);
    }
    function close() {
        panel.hidden = true;
        root.classList.remove('is-open');
        launcher.setAttribute('aria-expanded', 'false');
        launcher.focus({ preventScroll: true });
    }
    function autosize() { input.style.height = 'auto'; input.style.height = Math.min(120, input.scrollHeight) + 'px'; }

    // Restore this tab's conversation
    if (state.turns.length) {
        $('tmAiStart')?.remove();
        state.turns.forEach((t) => addMsg(t.role === 'user' ? 'user' : 'bot', t.text, { lead: t.lead }));
        addChips(state.suggestions);
    }

    launcher.addEventListener('click', open);
    $('tmAiClose').addEventListener('click', close);
    $('tmAiReset').addEventListener('click', () => {
        state = { token: '', turns: [] }; save();
        body.querySelectorAll('.tm-ai-msg:not(.tm-ai-greet), .tm-ai-chips.is-follow, .tm-ai-lead').forEach((n) => n.remove());
        input.focus();
    });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !panel.hidden) close(); });
    form.addEventListener('submit', (e) => { e.preventDefault(); send(input.value); });
    input.addEventListener('input', autosize);
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input.value); } });
    body.addEventListener('click', (e) => {
        const chip = e.target.closest('.tm-ai-chip');
        if (chip) send(chip.dataset.q);
    });

    // ---- Character life: eyes follow the cursor, wave hello, talk while replying
    const looks = root.querySelectorAll('.tima-look');
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!reduce && window.matchMedia('(hover: hover)').matches) {
        let raf = 0;
        window.addEventListener('pointermove', (e) => {
            if (raf) return;
            raf = requestAnimationFrame(() => {
                raf = 0;
                looks.forEach((g) => {
                    const r = g.closest('svg').getBoundingClientRect();
                    const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
                    const d = Math.max(1, Math.hypot(dx, dy));
                    g.style.setProperty('--ex', (dx / d * Math.min(4, d / 60)).toFixed(2) + 'px');
                    g.style.setProperty('--ey', (dy / d * Math.min(3, d / 60)).toFixed(2) + 'px');
                });
            });
        }, { passive: true });
    }
    const wave = () => { if (reduce) return; root.classList.add('is-waving'); setTimeout(() => root.classList.remove('is-waving'), 1900); };
    setTimeout(wave, 1500);
    launcher.addEventListener('mouseenter', wave);

    // ---- Page-aware suggestions
    const h1 = (document.querySelector('main h1, h1')?.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 60);
    const path = location.pathname;
    function pageQuestions() {
        if (!h1) return [];
        if (/^\/services\/(?!industries)[^/]+\/[^/]+\/$/.test(path)) return [`What does ${h1} include?`, `How does ${h1} work for my business?`, `Get a quote for ${h1}`];
        if (/^\/services\/industries\/[^/]+\/$/.test(path)) return [`How do you help ${h1} companies?`, `Which services suit ${h1}?`];
        if (/^\/services\/(?!industries)[^/]+\/$/.test(path)) return [`What's included in ${h1}?`, `Which ${h1} service do I need?`];
        if (/^\/insights\/[^/]+\/$/.test(path)) return ['Summarise this article for me', 'How can TM Solutech help with this?'];
        if (path.startsWith('/contact')) return ['What happens after I enquire?', 'How quickly do you reply?'];
        if (path.startsWith('/careers') || path.startsWith('/life-at')) return ['What roles are open?', 'What is it like to work at TM Solutech?'];
        return [];
    }
    const pageQs = root.dataset.pageChips === '1' ? pageQuestions() : [];
    const pageBox = $('tmAiPageChips');
    if (pageBox && pageQs.length) {
        pageBox.innerHTML = '<span class="tm-ai-start-title"><i class="fas fa-location-dot"></i> About this page</span>';
        pageQs.forEach((q) => { const b = document.createElement('button'); b.type = 'button'; b.className = 'tm-ai-chip tm-ai-chip-page'; b.dataset.q = q; b.textContent = q; pageBox.appendChild(b); });
        pageBox.hidden = false;
    }

    // ---- Pop-up: a random message (page-aware), with two quick questions
    let nudges = [];
    try { nudges = JSON.parse($('tmAiNudges')?.textContent || '[]').filter(Boolean); } catch (e) { nudges = []; }
    let quick = [];
    try { quick = JSON.parse($('tmAiQuick')?.textContent || '[]'); } catch (e) { quick = []; }
    const shownKey = 'tmAi.nudgeShown';
    let shownCount = 0;
    try { shownCount = parseInt(sessionStorage.getItem(shownKey) || '0', 10); } catch (e) { /* ignore */ }
    if (nudge && nudges.length && !state.turns.length && shownCount < 3) {
        const pageName = h1 || 'this page';
        let pool = nudges.filter((n) => !n.includes('{page}') || h1);
        const msg = pool[Math.floor(Math.random() * pool.length)].replace('{page}', pageName);
        setTimeout(() => {
            if (!panel.hidden || state.turns.length) return;
            nudge.querySelector('.tm-ai-nudge-text').textContent = msg;
            const chipsBox = nudge.querySelector('.tm-ai-nudge-chips');
            chipsBox.innerHTML = '';
            (pageQs.length ? pageQs : quick).slice(0, 2).forEach((q) => {
                const b = document.createElement('button'); b.type = 'button'; b.dataset.q = q; b.textContent = q; chipsBox.appendChild(b);
            });
            nudge.hidden = false;
            root.classList.add('is-waving'); setTimeout(() => root.classList.remove('is-waving'), 1900);
            try { sessionStorage.setItem(shownKey, String(shownCount + 1)); } catch (e) { /* ignore */ }
            setTimeout(() => { nudge.classList.add('is-leaving'); setTimeout(() => { nudge.hidden = true; nudge.classList.remove('is-leaving'); }, 400); }, 14000);
        }, (parseInt(root.dataset.nudgeDelay, 10) || 8) * 1000);
        nudge.addEventListener('click', (e) => {
            if (e.target.closest('.tm-ai-nudge-x')) { nudge.hidden = true; try { sessionStorage.setItem(shownKey, '9'); } catch (err) { /* ignore */ } return; }
            const chip = e.target.closest('[data-q]');
            open();
            if (chip) send(chip.dataset.q);
        });
    }
    // ---- Section-aware tips: as visitors scroll and pause on a section, Tima offers help about it
    const TOPICS = [
        [/industr|sector/i, 'Wondering if we work in your industry?', ['Do you work with my industry?', 'How do you help banks and BFSI?']],
        [/servic|solution|what we/i, 'Exploring our services? I can point you to the right one.', ['Which service fits my business?', 'What does Managed IT include?']],
        [/leader|team|director/i, 'Want to know who leads TM Solutech?', ['Who leads TM Solutech?', 'How long has the company been around?']],
        [/client|trusted|partner|brand/i, 'Curious who we work with?', ['Which brands do you work with?', 'Who are your clients?']],
        [/insight|article|blog|news/i, 'Want the short version of our latest insights?', ['Summarise your latest articles', 'Explain SEBI CSCRF simply']],
        [/why|different|choose|heritage/i, 'Comparing IT partners? Here is what sets us apart.', ['Why choose TM Solutech?', 'Do you provide 24/7 support?']],
        [/capabilit|technolog|stack/i, 'Need the full picture of our capabilities?', ['What can you manage end to end?', 'Do you support cloud and on-premise?']],
        [/process|how we work|deliver/i, 'Questions about how we deliver?', ['How long does a typical project take?', 'What happens after I enquire?']],
        [/faq|question/i, "Can't find your answer? Just ask me.", ['How is pricing structured?', 'How quickly can you start?']],
        [/contact|touch|consult/i, 'I can pass your details to the team right now.', ['I want a free consultation', 'Call me back today']],
    ];
    const tipKey = 'tmAi.tips';
    let tipsOff = false;
    try { tipsOff = sessionStorage.getItem(tipKey) === 'off'; } catch (e) { /* ignore */ }
    if (nudge && !tipsOff && 'IntersectionObserver' in window) {
        const seen = new Set();
        let lastTip = Date.now(), tipCount = 0, dwell = null;
        const showTip = (msg, qs) => {
            if (!panel.hidden || busy || tipCount >= 4 || Date.now() - lastTip < 20000) return false;
            nudge.querySelector('.tm-ai-nudge-text').textContent = msg;
            const box = nudge.querySelector('.tm-ai-nudge-chips');
            box.innerHTML = '';
            qs.forEach((q) => { const b = document.createElement('button'); b.type = 'button'; b.dataset.q = q; b.textContent = q; box.appendChild(b); });
            nudge.classList.remove('is-leaving');
            nudge.hidden = false;
            root.classList.add('is-waving'); setTimeout(() => root.classList.remove('is-waving'), 1900);
            lastTip = Date.now(); tipCount++;
            return true;
            clearTimeout(nudge._hide);
            nudge._hide = setTimeout(() => { nudge.classList.add('is-leaving'); setTimeout(() => { nudge.hidden = true; nudge.classList.remove('is-leaving'); }, 400); }, 12000);
        };
        const heads = Array.from(document.querySelectorAll('main h2, section h2')).filter((h) => !h.closest('.tm-ai'));
        const io = new IntersectionObserver((entries) => {
            entries.forEach((en) => {
                if (!en.isIntersecting) return;
                const text = en.target.textContent.trim();
                const topic = TOPICS.find(([re]) => re.test(text) || re.test(en.target.closest('section')?.className || ''));
                if (!topic || seen.has(topic[1])) return;
                clearTimeout(dwell);
                dwell = setTimeout(() => {          // only if the visitor actually pauses here
                    const r = en.target.getBoundingClientRect();
                    if (r.top < 0 || r.top > window.innerHeight * 0.8) return;
                    if (showTip(topic[1], topic[2])) seen.add(topic[1]);
                }, 2500);
            });
        }, { rootMargin: '-15% 0px -35% 0px' });
        heads.forEach((h) => io.observe(h));
        nudge.querySelector('.tm-ai-nudge-x').addEventListener('click', () => { try { sessionStorage.setItem(tipKey, 'off'); } catch (e) { /* ignore */ } tipCount = 99; });
        // the welcome pop-up counts as the first tip
        lastTip = Date.now() - 20000 + (parseInt(root.dataset.nudgeDelay, 10) || 8) * 1000 + 15000;
    }
})();
