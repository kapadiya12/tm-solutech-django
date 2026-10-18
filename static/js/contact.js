/* Contact page
   - Styled pop-ups: searchable service picker + country-code picker (all countries)
   - Live validation mirroring contact/forms.py (+ per-country phone lengths)
   - In-page submit, success state, draft autosave, copy buttons, office status */
(function () {
    'use strict';
    const form = document.getElementById('contactForm');
    if (!form) return;

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const mobileSheet = window.matchMedia('(max-width: 640px)');
    const readJSON = (id) => { try { return JSON.parse(document.getElementById(id).textContent); } catch (e) { return null; } };
    const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const fold = (s) => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

    /* =====================================================================
       POP-UP LIST (shared by service + country pickers)
       ===================================================================== */
    let openPop = null;
    const backdrop = document.createElement('div');
    backdrop.className = 'cf-pop-backdrop';
    document.body.appendChild(backdrop);
    backdrop.addEventListener('click', () => openPop && openPop.close());

    function createPopup({ anchor, items, groups, searchPlaceholder, renderItem, onPick, getSelected, title, wide, customOption }) {
        const pop = document.createElement('div');
        pop.className = 'cf-pop' + (wide ? ' cf-pop-wide' : '');
        pop.setAttribute('role', 'dialog');
        pop.setAttribute('aria-label', title);
        pop.setAttribute('data-lenis-prevent', '');   // let the list scroll natively (Lenis smooth-scroll ignores it)
        pop.innerHTML =
            '<div class="cf-pop-head"><strong>' + escapeHtml(title) + '</strong><button type="button" class="cf-pop-close" aria-label="Close"><i class="fas fa-xmark"></i></button></div>' +
            '<div class="cf-pop-search"><i class="fas fa-magnifying-glass" aria-hidden="true"></i><input type="text" autocomplete="off" spellcheck="false" placeholder="' + escapeHtml(searchPlaceholder) + '" aria-label="' + escapeHtml(searchPlaceholder) + '"><button type="button" class="cf-pop-clear" aria-label="Clear search" hidden><i class="fas fa-xmark"></i></button></div>' +
            '<ul class="cf-pop-list" role="listbox"></ul>' +
            '<p class="cf-pop-empty" hidden>No matches. Try another word.</p>';
        document.body.appendChild(pop);
        const search = pop.querySelector('input');
        const clearBtn = pop.querySelector('.cf-pop-clear');
        const list = pop.querySelector('.cf-pop-list');
        const empty = pop.querySelector('.cf-pop-empty');
        let visible = [];
        let active = -1;

        function render(q) {
            const query = fold(q.trim());
            visible = items.filter((it) => !query || it.search.includes(query));
            clearBtn.hidden = !q;
            if (customOption && q.trim()) {
                const extra = customOption(q.trim(), visible);
                if (extra) visible.push(extra);
            }
            let html = '';
            let lastGroup = null;
            visible.forEach((it, i) => {
                if (groups && !query && it.group !== lastGroup) {
                    lastGroup = it.group;
                    if (it.group) html += '<li class="cf-pop-group" role="presentation">' + (it.groupIcon ? '<i class="' + escapeHtml(it.groupIcon) + '"></i>' : '') + escapeHtml(it.group) + '</li>';
                }
                const sel = it.value === getSelected();
                html += '<li class="cf-pop-opt' + (sel ? ' is-selected' : '') + '" role="option" id="' + pop.dataset.uid + '-' + i + '" data-i="' + i + '" aria-selected="' + sel + '">' + renderItem(it, query) + (sel ? '<i class="fas fa-check cf-pop-tick" aria-hidden="true"></i>' : '') + '</li>';
            });
            list.innerHTML = html;
            empty.hidden = visible.length > 0;
            const selIndex = query ? -1 : visible.findIndex((it) => it.value === getSelected());
            setActive(selIndex >= 0 ? selIndex : 0, true);
        }

        function setActive(i, center) {
            const opts = list.querySelectorAll('.cf-pop-opt');
            if (!opts.length) { active = -1; return; }
            active = Math.max(0, Math.min(i, opts.length - 1));
            opts.forEach((o, k) => o.classList.toggle('is-active', k === active));
            const el = opts[active];
            search.setAttribute('aria-activedescendant', el.id);
            const top = el.offsetTop - list.offsetTop;
            if (center) list.scrollTop = top - list.clientHeight / 2 + el.offsetHeight / 2;
            else if (top < list.scrollTop) list.scrollTop = top - 6;
            else if (top + el.offsetHeight > list.scrollTop + list.clientHeight) list.scrollTop = top + el.offsetHeight - list.clientHeight + 6;
        }

        function position() {
            if (mobileSheet.matches) { pop.style.left = pop.style.top = pop.style.width = ''; return; }
            const r = anchor.getBoundingClientRect();
            const width = Math.max(r.width, wide ? 360 : 280);
            const left = Math.min(Math.max(12, r.left), window.innerWidth - width - 12);
            const spaceBelow = window.innerHeight - r.bottom;
            const openUp = spaceBelow < 300 && r.top > spaceBelow;
            pop.style.width = width + 'px';
            pop.style.left = left + 'px';
            pop.classList.toggle('is-up', openUp);
            pop.style.top = openUp ? '' : (r.bottom + 8) + 'px';
            pop.style.bottom = openUp ? (window.innerHeight - r.top + 8) + 'px' : '';
        }

        const api = {
            open() {
                if (openPop && openPop !== api) openPop.close();
                openPop = api;
                search.value = '';
                render('');
                position();
                pop.classList.add('is-open');
                backdrop.classList.toggle('is-on', mobileSheet.matches);
                document.documentElement.classList.toggle('cf-pop-locked', mobileSheet.matches);
                anchor.setAttribute('aria-expanded', 'true');
                setTimeout(() => search.focus({ preventScroll: true }), mobileSheet.matches ? 260 : 20);
                window.addEventListener('scroll', position, { passive: true });
                window.addEventListener('resize', position, { passive: true });
            },
            close(returnFocus = true) {
                if (openPop !== api) return;
                openPop = null;
                pop.classList.remove('is-open');
                backdrop.classList.remove('is-on');
                document.documentElement.classList.remove('cf-pop-locked');
                anchor.setAttribute('aria-expanded', 'false');
                window.removeEventListener('scroll', position);
                window.removeEventListener('resize', position);
                if (returnFocus) anchor.focus({ preventScroll: true });
            },
            toggle() { openPop === api ? api.close() : api.open(); },
            isOpen: () => openPop === api,
        };
        pop.dataset.uid = 'cfp' + Math.random().toString(36).slice(2, 8);
        list.setAttribute('id', pop.dataset.uid + '-list');
        search.setAttribute('aria-controls', pop.dataset.uid + '-list');

        search.addEventListener('input', () => render(search.value));
        clearBtn.addEventListener('click', () => { search.value = ''; render(''); search.focus(); });
        search.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') { e.preventDefault(); setActive(active + 1); }
            else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
            else if (e.key === 'Home') { e.preventDefault(); setActive(0); }
            else if (e.key === 'End') { e.preventDefault(); setActive(visible.length - 1); }
            else if (e.key === 'Enter') { e.preventDefault(); if (visible[active]) { onPick(visible[active]); api.close(); } }
            else if (e.key === 'Escape') { e.preventDefault(); if (search.value) { search.value = ''; render(''); } else api.close(); }
            else if (e.key === 'Tab') { api.close(false); }
        });
        list.addEventListener('mousemove', (e) => {
            const li = e.target.closest('.cf-pop-opt');
            if (li && Number(li.dataset.i) !== active) setActive(Number(li.dataset.i));
        });
        list.addEventListener('click', (e) => {
            const li = e.target.closest('.cf-pop-opt');
            if (!li) return;
            onPick(visible[Number(li.dataset.i)]);
            api.close();
        });
        pop.querySelector('.cf-pop-close').addEventListener('click', () => api.close());
        document.addEventListener('pointerdown', (e) => {
            if (openPop === api && !pop.contains(e.target) && !anchor.contains(e.target)) api.close(false);
        });
        return api;
    }

    const highlight = (text, q) => {
        if (!q) return escapeHtml(text);
        const i = fold(text).indexOf(q);
        if (i < 0) return escapeHtml(text);
        return escapeHtml(text.slice(0, i)) + '<mark>' + escapeHtml(text.slice(i, i + q.length)) + '</mark>' + escapeHtml(text.slice(i + q.length));
    };

    /* ---------- Service picker ---------- */
    const serviceSelect = form.querySelector('select[data-combo]');
    if (serviceSelect) {
        const icons = readJSON('cfServiceIcons') || {};
        const field = serviceSelect.closest('.cf-field');
        const items = [];
        Array.from(serviceSelect.options).forEach((opt) => {
            const group = opt.parentElement.tagName === 'OPTGROUP' ? opt.parentElement.label : '';
            items.push({ value: opt.value, label: opt.textContent, group, groupIcon: icons[group] || (group === 'Other' ? 'fas fa-compass' : ''), search: fold(opt.textContent + ' ' + group) });
        });
        const trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'cf-input cf-combo-trigger';
        trigger.setAttribute('aria-haspopup', 'listbox');
        trigger.setAttribute('aria-expanded', 'false');
        trigger.setAttribute('aria-labelledby', 'cfServiceLabel cfServiceValue');
        trigger.innerHTML = '<span class="cf-combo-value" id="cfServiceValue"></span>';
        field.querySelector('label').id = 'cfServiceLabel';
        serviceSelect.classList.add('cf-native-hidden');
        serviceSelect.tabIndex = -1;
        serviceSelect.setAttribute('aria-hidden', 'true');
        serviceSelect.after(trigger);
        field.classList.add('is-enhanced');

        const sync = () => {
            const opt = serviceSelect.options[serviceSelect.selectedIndex];
            const has = !!serviceSelect.value;
            const otherText = document.getElementById('id_service_other');
            const label = serviceSelect.value === '__other__' && otherText && otherText.value.trim() ? 'Other: ' + otherText.value.trim() : (opt ? opt.textContent : '');
            trigger.querySelector('.cf-combo-value').textContent = has ? label : 'Select a service (optional)';
            trigger.classList.toggle('is-placeholder', !has);
        };
        sync();
        const otherWrap = document.getElementById('cfOtherWrap');
        const otherInput = document.getElementById('id_service_other');
        const showOther = (on, focus) => {
            if (!otherWrap) return;
            otherWrap.classList.toggle('is-shown', on);
            if (!on) { otherInput.value = ''; setError('service_other', ''); }
            else if (focus) setTimeout(() => otherInput.focus(), 60);
        };
        const pop = createPopup({
            anchor: trigger, items, groups: true, wide: true,
            customOption: (q, matches) => (matches.some((m) => fold(m.label) === fold(q)) ? null
                : { value: '__custom__', raw: q, label: q, custom: true, search: '' }),
            title: 'Service of interest',
            searchPlaceholder: 'Search 37 services…',
            getSelected: () => serviceSelect.value,
            renderItem: (it, q) => it.custom
                ? '<span class="cf-pop-custom-icon" aria-hidden="true"><i class="fas fa-pen"></i></span><span class="cf-pop-text">Use “' + escapeHtml(it.raw) + '”<small>Not in the list? We’ll note it as your service.</small></span>'
                : it.value === '__other__' ? '<span class="cf-pop-custom-icon" aria-hidden="true"><i class="fas fa-pen"></i></span><span class="cf-pop-text">' + highlight(it.label, q) + '</span>'
                : it.value ? '<span class="cf-pop-text">' + highlight(it.label, q) + (q && it.group ? '<small>' + escapeHtml(it.group) + '</small>' : '') + '</span>'
                                              : '<span class="cf-pop-text cf-pop-muted">' + escapeHtml(it.label) + '</span>',
            onPick: (it) => {
                if (it.custom) {
                    serviceSelect.value = '__other__';
                    otherInput.value = it.raw;
                    showOther(true);
                    touched.add('service_other'); check('service_other');
                } else {
                    serviceSelect.value = it.value;
                    showOther(it.value === '__other__', true);
                }
                serviceSelect.dispatchEvent(new Event('change', { bubbles: true }));
                sync();
                saveDraft();
            },
        });
        trigger.addEventListener('click', () => pop.toggle());
        trigger.addEventListener('keydown', (e) => {
            if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(e.key)) { e.preventDefault(); pop.open(); }
        });
        serviceSelect.addEventListener('change', sync);
        if (otherInput) otherInput.addEventListener('input', sync);
        form.addEventListener('reset', () => setTimeout(() => showOther(false)));
        form.addEventListener('reset', () => setTimeout(sync));
    }

    /* ---------- Country-code picker ---------- */
    const countrySelect = form.querySelector('select[data-country-select]');
    const phoneInput = form.querySelector('#id_phone');
    const countries = readJSON('cfCountries') || [];
    const byIso = Object.fromEntries(countries.map((c) => [c.iso, c]));
    let regionNames = null;
    try { regionNames = new Intl.DisplayNames([navigator.language || 'en', 'en'], { type: 'region' }); } catch (e) { regionNames = null; }
    const countryName = (iso) => { try { return (regionNames && regionNames.of(iso)) || iso; } catch (e) { return iso; } };

    // Flag emoji where the OS can draw them (macOS/iOS/Android); ISO badge otherwise (Windows)
    const flagSupported = (() => {
        try {
            const c = document.createElement('canvas'); c.width = c.height = 16;
            const x = c.getContext('2d'); x.textBaseline = 'top'; x.font = '14px sans-serif';
            x.fillText('\u{1F1EE}\u{1F1F3}', 0, 0);
            const d = x.getImageData(0, 0, 16, 16).data;
            for (let i = 0; i < d.length; i += 4) if (d[i] !== d[i + 1] || d[i + 1] !== d[i + 2]) return true; // coloured pixels
            return false;
        } catch (e) { return false; }
    })();
    const flag = (iso) => flagSupported
        ? '<span class="cf-flag" aria-hidden="true">' + String.fromCodePoint(...iso.split('').map((ch) => 0x1F1E6 + ch.charCodeAt(0) - 65)) + '</span>'
        : '<span class="cf-flag cf-flag-iso" aria-hidden="true">' + iso + '</span>';

    let currentCountry = null;
    let setCountryFn = null;
    if (countrySelect && phoneInput && countries.length) {
        const wrap = countrySelect.closest('.cf-phone');
        const field = countrySelect.closest('.cf-field');
        const items = countries.map((c) => ({ value: c.iso, label: countryName(c.iso), dial: c.dial, search: fold(countryName(c.iso) + ' ' + c.iso + ' +' + c.dial + ' ' + c.dial) }))
            .sort((a, b) => a.label.localeCompare(b.label));
        // Pin the default country first
        const pinned = countrySelect.value;
        const pinIdx = items.findIndex((it) => it.value === pinned);
        if (pinIdx > 0) items.unshift(items.splice(pinIdx, 1)[0]);

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'cf-cc';
        btn.setAttribute('aria-haspopup', 'listbox');
        btn.setAttribute('aria-expanded', 'false');
        countrySelect.classList.add('cf-native-hidden');
        countrySelect.tabIndex = -1;
        countrySelect.setAttribute('aria-hidden', 'true');
        wrap.prepend(btn);
        field.classList.add('is-enhanced');

        const setCountry = (iso, keepFocus) => {
            const c = byIso[iso] || byIso.IN || countries[0];
            currentCountry = c;
            countrySelect.value = c.iso;
            btn.innerHTML = flag(c.iso) + '<span class="cf-cc-dial">+' + c.dial + '</span><i class="fas fa-chevron-down" aria-hidden="true"></i>';
            btn.setAttribute('aria-label', 'Country code: ' + countryName(c.iso) + ' +' + c.dial + '. Change');
            phoneInput.setAttribute('data-example', c.example || '');
            const hint = field.querySelector('.cf-hint');
            if (hint) hint.textContent = c.example ? 'Optional · e.g. ' + c.example : 'Optional';
            if (keepFocus) phoneInput.focus();
        };
        setCountry(countrySelect.value);
        setCountryFn = setCountry;

        const pop = createPopup({
            anchor: btn, items, groups: false,
            title: 'Country code',
            searchPlaceholder: 'Search country or code…',
            getSelected: () => countrySelect.value,
            renderItem: (it, q) => flag(it.value) + '<span class="cf-pop-text">' + highlight(it.label, q) + '</span><span class="cf-pop-dial">+' + it.dial + '</span>',
            onPick: (it) => { setCountry(it.value); if (phoneTouched()) check('phone'); setTimeout(() => phoneInput.focus(), 30); saveDraft(); },
        });
        btn.addEventListener('click', () => pop.toggle());
        btn.addEventListener('keydown', (e) => { if (['ArrowDown', 'ArrowUp'].includes(e.key)) { e.preventDefault(); pop.open(); } });

        // Typing or pasting "+44 7400…" switches the country automatically
        const dialSorted = countries.slice().sort((a, b) => String(b.dial).length - String(a.dial).length);
        phoneInput.addEventListener('input', () => {
            const v = phoneInput.value.trim();
            if (!v.startsWith('+')) return;
            const digits = v.slice(1).replace(/\D/g, '');
            const match = dialSorted.find((c) => digits.startsWith(String(c.dial)) && digits.length > String(c.dial).length);
            if (!match) return;
            const iso = match.dial === currentCountry.dial ? currentCountry.iso : match.iso;
            setCountry(iso);
            phoneInput.value = digits.slice(String(match.dial).length);
        });
        form.addEventListener('reset', () => setTimeout(() => setCountry(pinned)));
    }

    /* =====================================================================
       VALIDATION
       ===================================================================== */
    const MIN = parseInt(form.dataset.messageMin, 10) || 20;
    const MAX = parseInt(form.dataset.messageMax, 10) || 2000;
    const NAME_RE = /^\p{L}+(?:(?:\. ?|[ '\-])\p{L}+)*\.?$/u;
    const EMAIL_RE = /^(?!.*\.\.)[A-Za-z0-9._%+\-]+@[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?)*\.[A-Za-z]{2,24}$/;
    const LETTERS = /\p{L}/gu;
    const REPEAT_RE = /(.)\1{5,}/;
    const URL_RE = /(https?:\/\/|www\.)/gi;
    const squash = (v) => v.replace(/\s+/g, ' ').trim();
    const phoneTouched = () => touched.has('phone');

    const rules = {
        name(v) {
            v = squash(v);
            if (!v) return 'Please enter your full name.';
            if (v.length < 2) return 'Your name looks too short.';
            if (v.length > 100) return 'Please keep your name under 100 characters.';
            if (!NAME_RE.test(v)) return 'Use letters only. Spaces, dots, hyphens and apostrophes are fine.';
            if ((v.match(LETTERS) || []).length < 2 || REPEAT_RE.test(v.toLowerCase())) return 'Please enter your real name.';
            return '';
        },
        company(v) {
            v = squash(v);
            if (!v) return '';
            if (v.length < 2) return 'Your company name looks too short.';
            if (v.length > 150) return 'Please keep the company name under 150 characters.';
            if (/(https?:\/\/|www\.)/i.test(v)) return 'Please enter the company name, not a link.';
            if (!(v.match(LETTERS) || []).length) return 'A company name needs at least one letter.';
            return '';
        },
        email(v) {
            v = v.trim();
            if (!v) return 'Please enter your work email.';
            if (v.length > 254 || !EMAIL_RE.test(v)) return 'Please enter a valid email address, like name@company.com.';
            return '';
        },
        phone(v) {
            v = v.trim();
            if (!v) return '';
            if (!/^[\d\s\-()]+$/.test(v)) return 'Use digits only. Spaces and dashes are fine.';
            let digits = v.replace(/\D/g, '');
            const lengths = (currentCountry && currentCountry.lengths) || [];
            if (!lengths.length) return digits.length >= 4 && digits.length <= 15 ? '' : 'Please enter a valid phone number.';
            if (lengths.includes(digits.length)) return '';
            if (digits.startsWith('0') && lengths.includes(digits.length - 1)) return ''; // trunk prefix, e.g. UK 07…
            const min = Math.min(...lengths), max = Math.max(...lengths);
            const name = currentCountry ? countryName(currentCountry.iso) : 'this country';
            return min === max ? `Numbers in ${name} have ${min} digits.` : `Numbers in ${name} have ${min} to ${max} digits.`;
        },
        message(v) {
            v = v.trim();
            if (!v) return 'Please tell us a little about what you need.';
            if (v.length < MIN) return `Please add a little more detail (at least ${MIN} characters).`;
            if (v.length > MAX) return `Please keep your message under ${MAX} characters.`;
            if ((v.match(LETTERS) || []).length < 10 || v.split(/\s+/).length < 3) return 'Please describe what you need in a few words.';
            if (REPEAT_RE.test(v)) return 'Please remove the repeated characters.';
            if ((v.match(URL_RE) || []).length > 3) return 'Please remove some links. Messages with many links are blocked as spam.';
            return '';
        },
        service_other(v) {
            const sel = control('service');
            if (!sel || sel.value !== '__other__') return '';
            v = squash(v);
            if (v.length < 2) return 'Please tell us which service you need.';
            if (/(https?:\/\/|www\.)/i.test(v)) return 'Please describe the service, not a link.';
            return '';
        },
        consent(_, el) { return el.checked ? '' : 'Please agree so we can contact you about your enquiry.'; },
    };

    const fieldBox = (name) => form.querySelector(`[data-field="${name}"]`);
    const control = (name) => form.querySelector(`[name="${name}"]`);

    function setError(name, msg) {
        const box = fieldBox(name);
        const el = control(name);
        const err = form.querySelector(`#err_${name}`);
        if (!box || !el) return;
        if (err) err.textContent = msg || '';
        box.classList.toggle('is-invalid', !!msg);
        const filled = el.type === 'checkbox' ? false : el.value.trim() !== '';
        box.classList.toggle('is-valid', !msg && filled && name !== 'service');
        if (msg) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid');
    }

    function check(name) {
        const el = control(name);
        if (!el || !rules[name]) return '';
        const msg = rules[name](el.value || '', el);
        setError(name, msg);
        return msg;
    }

    const touched = new Set();
    Object.keys(rules).forEach((name) => {
        const el = control(name);
        if (!el) return;
        el.addEventListener(el.type === 'checkbox' ? 'change' : 'blur', () => { touched.add(name); check(name); });
        el.addEventListener('input', () => { if (touched.has(name)) check(name); saveDraft(); });
    });
    /* ---------- Typing guards ---------- */
    const nameEl = control('name');
    if (nameEl) nameEl.addEventListener('input', () => {
        const clean = nameEl.value.replace(/[^\p{L}\p{M} .'\-]/gu, '');
        if (clean !== nameEl.value) { nameEl.value = clean; flashHint('name', 'Names can only contain letters.'); }
    });
    const phoneEl = control('phone');
    if (phoneEl) phoneEl.addEventListener('input', () => {
        if (phoneEl.value.trim().startsWith('+')) return; // handled by country auto-detect
        let v = phoneEl.value.replace(/[^\d\s\-()]/g, '');
        const lengths = (currentCountry && currentCountry.lengths) || [];
        const max = lengths.length ? Math.max(...lengths) + (v.replace(/\D/g, '').startsWith('0') ? 1 : 0) : 15;
        let digits = 0;
        v = Array.from(v).filter((ch) => (/\d/.test(ch) ? ++digits <= max : true)).join('');
        if (v !== phoneEl.value) { phoneEl.value = v; if (digits > max) flashHint('phone', 'That is the maximum length for this country.'); }
    });
    function flashHint(name, text) {
        const err = form.querySelector('#err_' + name);
        if (!err || fieldBox(name).classList.contains('is-invalid')) return;
        err.textContent = text;
        clearTimeout(err._t);
        err._t = setTimeout(() => { if (!fieldBox(name).classList.contains('is-invalid')) err.textContent = ''; }, 1800);
    }

    // "Did you mean …@gmail.com?" for common domain typos
    const DOMAINS = ['gmail.com', 'yahoo.com', 'yahoo.co.in', 'outlook.com', 'hotmail.com', 'icloud.com', 'rediffmail.com', 'live.com', 'protonmail.com', 'zoho.com'];
    const lev = (a, b) => {
        const d = Array.from({ length: a.length + 1 }, (_, i) => [i]);
        for (let j = 1; j <= b.length; j++) d[0][j] = j;
        for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++)
            d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        return d[a.length][b.length];
    };
    const emailEl = control('email');
    if (emailEl) {
        const tip = document.createElement('button');
        tip.type = 'button';
        tip.className = 'cf-suggest';
        tip.hidden = true;
        fieldBox('email').appendChild(tip);
        emailEl.addEventListener('blur', () => {
            const v = emailEl.value.trim().toLowerCase();
            const at = v.lastIndexOf('@');
            tip.hidden = true;
            if (at < 1) return;
            const domain = v.slice(at + 1);
            if (!domain || DOMAINS.includes(domain)) return;
            const best = DOMAINS.map((d) => [d, lev(domain, d)]).sort((a, b) => a[1] - b[1])[0];
            if (best && best[1] > 0 && best[1] <= 2) {
                const fixed = v.slice(0, at + 1) + best[0];
                tip.innerHTML = '<i class="fas fa-wand-magic-sparkles" aria-hidden="true"></i> Did you mean <strong>' + escapeHtml(fixed) + '</strong>?';
                tip.dataset.fix = fixed;
                tip.hidden = false;
            }
        });
        tip.addEventListener('click', () => { emailEl.value = tip.dataset.fix; tip.hidden = true; check('email'); saveDraft(); });
    }

    ['name', 'company', 'email'].forEach((name) => {
        const el = control(name);
        if (el) el.addEventListener('blur', () => { el.value = name === 'email' ? el.value.trim() : squash(el.value); });
    });

    // Character counter
    const message = form.querySelector('#id_message');
    const counterWrap = form.querySelector('#cf_counter');
    const counter = counterWrap && counterWrap.querySelector('[data-count]');
    function updateCounter() {
        if (!message || !counter) return;
        const n = message.value.trim().length;
        counter.textContent = message.value.length;
        counterWrap.classList.toggle('is-low', n > 0 && n < MIN);
        counterWrap.classList.toggle('is-ok', n >= MIN);
    }
    if (message) { message.addEventListener('input', updateCounter); updateCounter(); }

    /* ---------- Draft autosave ---------- */
    const DRAFT_KEY = 'tmContactDraft';
    const draftFields = ['name', 'company', 'email', 'phone', 'phone_country', 'message', 'service', 'service_other'];
    function saveDraft() {
        try {
            const data = {};
            draftFields.forEach((n) => { const el = control(n); if (el) data[n] = el.value; });
            localStorage.setItem(DRAFT_KEY, JSON.stringify(data));
        } catch (e) { /* storage unavailable */ }
    }
    function clearDraft() { try { localStorage.removeItem(DRAFT_KEY); } catch (e) { /* ignore */ } }
    (function restoreDraft() {
        if (form.querySelector('.is-invalid')) return; // server returned errors: keep its values
        let data = null;
        try { data = JSON.parse(localStorage.getItem(DRAFT_KEY) || 'null'); } catch (e) { data = null; }
        if (!data) return;
        draftFields.forEach((n) => {
            const el = control(n);
            if (!el || !data[n]) return;
            if (n === 'phone_country') { if (setCountryFn && byIso[data[n]]) setCountryFn(data[n]); }
            else if (n === 'service') {
                el.value = data[n];
                const wrap = document.getElementById('cfOtherWrap');
                if (wrap) wrap.classList.toggle('is-shown', data[n] === '__other__');
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
            else if (!el.value) el.value = data[n];
        });
        updateCounter();
    })();

    /* =====================================================================
       SUBMIT
       ===================================================================== */
    const card = document.getElementById('contactFormCard');
    const alertBox = document.getElementById('cfAlert');
    const alertText = document.getElementById('cfAlertText');
    const submit = document.getElementById('cfSubmit');
    const success = document.getElementById('cfSuccess');
    const successText = document.getElementById('cfSuccessText');
    const tokenInput = form.querySelector('input[name="form_token"]');
    const submitLabel = form.dataset.submitLabel || 'Send message';

    const showAlert = (text) => { if (alertBox) { alertText.textContent = text || ''; alertBox.hidden = false; } };
    const hideAlert = () => { if (alertBox) alertBox.hidden = true; };
    function shake(box) {
        if (reduceMotion || !box) return;
        box.classList.remove('shake'); void box.offsetWidth; box.classList.add('shake');
    }
    function focusField(name) {
        const box = fieldBox(name);
        const target = (box && box.querySelector('.cf-combo-trigger')) || control(name);
        if (target) target.focus();
    }
    function setLoading(on) {
        submit.classList.toggle('is-loading', on);
        submit.disabled = on;
        submit.querySelector('.cf-submit-label').textContent = on ? 'Sending…' : submitLabel;
    }
    function scrollToCard() {
        const top = card.getBoundingClientRect().top + window.scrollY - ((document.querySelector('.navbar') || {}).offsetHeight || 0) - 24;
        if (window.tmLenis) window.tmLenis.scrollTo(Math.max(top, 0), { duration: 0.9 });
        else window.scrollTo({ top: Math.max(top, 0), behavior: reduceMotion ? 'auto' : 'smooth' });
    }
    function showSuccess(text) {
        clearDraft();
        form.hidden = true;
        if (successText && text) successText.textContent = text;
        success.hidden = false;
        success.focus({ preventScroll: true });
        scrollToCard();
        flash('Message sent', 'success');
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        hideAlert();
        const invalid = Object.keys(rules).filter((name) => { touched.add(name); return !!check(name); });
        if (invalid.length) {
            showAlert(invalid.length === 1 ? '1 field needs your attention.' : `${invalid.length} fields need your attention.`);
            invalid.forEach((n) => shake(fieldBox(n)));
            focusField(invalid[0]);
            return;
        }
        if (!window.fetch || !window.FormData) { form.submit(); return; }
        setLoading(true);
        try {
            const res = await fetch(form.action, {
                method: 'POST', body: new FormData(form),
                headers: { 'X-Requested-With': 'fetch' }, credentials: 'same-origin',
            });
            const data = await res.json().catch(() => null);
            if (data && data.form_token && tokenInput) tokenInput.value = data.form_token;
            if (res.ok && data && data.ok) {
                showSuccess(data.message);
            } else if (data && data.errors) {
                const general = (data.errors.__all__ || []).join(' ');
                const names = Object.keys(data.errors).filter((k) => k !== '__all__');
                names.forEach((n) => { setError(n, data.errors[n][0]); shake(fieldBox(n)); });
                showAlert(general || 'Please fix the highlighted fields.');
                if (names.length) focusField(names[0]);
                flash(general || 'Please check the highlighted fields', 'error');
            } else {
                showAlert('Something went wrong on our side. Please try again, or email us directly.');
                flash('Could not send. Please try again', 'error');
            }
        } catch (e) {
            showAlert('We could not reach the server. Check your connection and try again.');
            flash('You appear to be offline', 'error');
        } finally {
            setLoading(false);
        }
    });

    const again = document.getElementById('cfAgain');
    if (again) again.addEventListener('click', () => {
        form.reset();
        form.querySelectorAll('.is-valid, .is-invalid').forEach((el) => el.classList.remove('is-valid', 'is-invalid'));
        form.querySelectorAll('.cf-error').forEach((el) => { el.textContent = ''; });
        touched.clear();
        updateCounter();
        success.hidden = true;
        form.hidden = false;
        setTimeout(() => focusField('name'), 30);
    });

    /* =====================================================================
       TOAST · COPY · OFFICE STATUS
       ===================================================================== */
    const toast = document.getElementById('cfToast');
    let toastTimer = null;
    function flash(text, tone) {
        if (!toast) return;
        const icon = tone === 'error' ? 'fa-circle-exclamation' : 'fa-circle-check';
        toast.className = 'cf-toast' + (tone === 'error' ? ' is-error' : '');
        toast.innerHTML = '<i class="fas ' + icon + '" aria-hidden="true"></i>' + escapeHtml(text);
        toast.hidden = false;
        requestAnimationFrame(() => toast.classList.add('is-on'));
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => { toast.classList.remove('is-on'); setTimeout(() => { toast.hidden = true; }, 300); }, 2200);
    }
    document.querySelectorAll('[data-copy]').forEach((btn) => {
        btn.addEventListener('click', async () => {
            const value = btn.dataset.copy;
            try {
                if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(value);
                else {
                    const ta = document.createElement('textarea');
                    ta.value = value; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
                    document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
                }
                btn.classList.add('is-copied');
                btn.innerHTML = '<i class="fas fa-check"></i>';
                flash('Copied ' + value, 'success');
                setTimeout(() => { btn.classList.remove('is-copied'); btn.innerHTML = '<i class="far fa-copy"></i>'; }, 1600);
            } catch (e) { flash('Press Ctrl+C to copy', 'error'); }
        });
    });

    const pill = document.querySelector('[data-office-status]');
    if (pill && window.Intl) {
        const days = (pill.dataset.days || '').split(',').map(Number);
        const toMin = (hm) => { const [h, m] = (hm || '0:0').split(':').map(Number); return h * 60 + m; };
        const openAt = toMin(pill.dataset.open), closeAt = toMin(pill.dataset.close);
        const dayIndex = { Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6, Sun: 7 };
        const update = () => {
            const parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Kolkata', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
            const get = (t) => (parts.find((p) => p.type === t) || {}).value;
            const mins = parseInt(get('hour'), 10) * 60 + parseInt(get('minute'), 10);
            const open = days.includes(dayIndex[get('weekday')]) && mins >= openAt && mins < closeAt;
            pill.textContent = open ? 'Open now' : 'Closed now';
            pill.classList.toggle('is-open', open);
            pill.classList.toggle('is-closed', !open);
            pill.hidden = false;
        };
        update();
        setInterval(update, 60000);
    }
})();
