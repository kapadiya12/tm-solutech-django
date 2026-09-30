/* ==========================================================================
   Dashboard editor helpers
   - Icon picker        : <input data-icon-picker>
   - Auto slug + URL    : <input data-slug-from="id_title">
   - Character counters : <input|textarea data-maxchars="160">
   - Row repeaters      : <div data-repeater="field_name" data-schema='[...]'>
   - Section nav, unsaved-changes guard
   ========================================================================== */
(function () {
    'use strict';

    // Curated Font Awesome 6 (free) icons for an IT services company, grouped for browsing.
    const ICONS = {
        'Cloud & Infrastructure': ['cloud', 'cloud-arrow-up', 'cloud-arrow-down', 'server', 'database', 'hard-drive', 'network-wired', 'sitemap', 'diagram-project', 'layer-group', 'cubes', 'cube', 'box-archive', 'boxes-stacked', 'warehouse', 'microchip', 'memory', 'plug', 'bolt', 'gauge-high', 'gauge', 'temperature-half', 'fan'],
        'Security': ['shield-halved', 'shield', 'shield-virus', 'user-shield', 'lock', 'unlock', 'key', 'fingerprint', 'user-lock', 'eye', 'eye-slash', 'bug', 'bug-slash', 'virus', 'triangle-exclamation', 'circle-exclamation', 'fire', 'fire-extinguisher', 'mask', 'user-secret', 'id-card', 'passport'],
        'Networking & Devices': ['wifi', 'tower-broadcast', 'satellite-dish', 'signal', 'ethernet', 'route', 'globe', 'earth-asia', 'laptop', 'desktop', 'mobile-screen', 'tablet-screen-button', 'print', 'keyboard', 'computer', 'house-laptop', 'headset', 'phone', 'video', 'camera'],
        'Software & Data': ['code', 'terminal', 'laptop-code', 'file-code', 'window-maximize', 'table-columns', 'chart-line', 'chart-pie', 'chart-column', 'chart-simple', 'magnifying-glass-chart', 'robot', 'brain', 'wand-magic-sparkles', 'arrows-rotate', 'rotate', 'sync', 'code-branch', 'code-merge', 'bars-progress', 'list-check', 'clipboard-check'],
        'Business & Support': ['briefcase', 'building', 'city', 'industry', 'landmark', 'building-columns', 'handshake', 'handshake-angle', 'users', 'user-tie', 'people-group', 'user-gear', 'users-gear', 'headset', 'life-ring', 'comments', 'envelope', 'calendar-check', 'clock', 'stopwatch', 'money-bill-trend-up', 'sack-dollar', 'coins', 'scale-balanced', 'gavel', 'file-contract', 'file-shield'],
        'Health, Education & More': ['heart-pulse', 'hospital', 'kit-medical', 'pills', 'flask', 'dna', 'graduation-cap', 'school', 'book', 'truck', 'truck-fast', 'plane', 'store', 'cart-shopping', 'gears', 'gear', 'screwdriver-wrench', 'wrench', 'toolbox', 'hammer'],
        'Symbols': ['check', 'circle-check', 'star', 'award', 'medal', 'trophy', 'rocket', 'lightbulb', 'bullseye', 'crosshairs', 'flag', 'thumbs-up', 'heart', 'infinity', 'leaf', 'seedling', 'recycle', 'arrow-trend-up', 'arrow-right', 'bolt-lightning', 'fire-flame-curved', 'gem', 'crown', 'puzzle-piece'],
        'Brands': ['fab fa-microsoft', 'fab fa-windows', 'fab fa-aws', 'fab fa-google', 'fab fa-linux', 'fab fa-apple', 'fab fa-android', 'fab fa-docker', 'fab fa-python', 'fab fa-java', 'fab fa-cloudflare', 'fab fa-github', 'fab fa-linkedin', 'fab fa-whatsapp'],
    };
    const toClass = (name) => (name.includes(' ') ? name : 'fas fa-' + name);
    const escapeHtml = (v) => String(v == null ? '' : v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

    /* ---------- Icon picker ---------- */
    let pickerEl = null;
    let pickerTarget = null;

    function buildPicker() {
        pickerEl = document.createElement('div');
        pickerEl.className = 'ip-modal';
        pickerEl.hidden = true;
        pickerEl.innerHTML =
            '<div class="ip-backdrop" data-ip-close></div>' +
            '<div class="ip-panel" role="dialog" aria-modal="true" aria-label="Choose an icon">' +
                '<div class="ip-head"><div><h3>Choose an icon</h3><p>Click an icon to use it. Icons appear on the website in the brand colours.</p></div>' +
                '<button type="button" class="ip-close" data-ip-close aria-label="Close"><i class="fas fa-xmark"></i></button></div>' +
                '<div class="ip-search"><i class="fas fa-magnifying-glass"></i><input type="search" placeholder="Search icons, e.g. cloud, lock, users…" aria-label="Search icons"></div>' +
                '<div class="ip-body" data-lenis-prevent></div>' +
                '<div class="ip-foot"><span>More icons: <a href="https://fontawesome.com/search?o=r&m=free" target="_blank" rel="noopener">fontawesome.com</a> — copy a class like <code>fas fa-cloud</code> and paste it in the box.</span></div>' +
            '</div>';
        document.body.appendChild(pickerEl);
        const body = pickerEl.querySelector('.ip-body');
        body.innerHTML = Object.entries(ICONS).map(([group, list]) =>
            '<div class="ip-group" data-group><h4>' + escapeHtml(group) + '</h4><div class="ip-grid">' +
            list.map((name) => {
                const cls = toClass(name);
                const label = cls.replace(/^fa[bs] fa-/, '').replace(/-/g, ' ');
                return '<button type="button" class="ip-icon" data-icon="' + cls + '" data-label="' + label + '" title="' + label + '"><i class="' + cls + '"></i><span>' + label + '</span></button>';
            }).join('') + '</div></div>'
        ).join('');

        const search = pickerEl.querySelector('.ip-search input');
        search.addEventListener('input', () => {
            const q = search.value.trim().toLowerCase();
            pickerEl.querySelectorAll('.ip-icon').forEach((b) => { b.hidden = q && !b.dataset.label.includes(q) && !b.dataset.icon.includes(q); });
            pickerEl.querySelectorAll('[data-group]').forEach((g) => { g.hidden = !g.querySelector('.ip-icon:not([hidden])'); });
        });
        body.addEventListener('click', (e) => {
            const btn = e.target.closest('.ip-icon');
            if (!btn || !pickerTarget) return;
            pickerTarget.value = btn.dataset.icon;
            pickerTarget.dispatchEvent(new Event('input', { bubbles: true }));
            pickerTarget.dispatchEvent(new Event('change', { bubbles: true }));
            closePicker();
        });
        pickerEl.querySelectorAll('[data-ip-close]').forEach((el) => el.addEventListener('click', closePicker));
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !pickerEl.hidden) closePicker(); });
    }
    function openPicker(input) {
        if (!pickerEl) buildPicker();
        pickerTarget = input;
        pickerEl.hidden = false;
        pickerEl.querySelectorAll('.ip-icon').forEach((b) => b.classList.toggle('is-selected', b.dataset.icon === input.value.trim()));
        const search = pickerEl.querySelector('.ip-search input');
        search.value = '';
        search.dispatchEvent(new Event('input'));
        requestAnimationFrame(() => pickerEl.classList.add('is-open'));
        setTimeout(() => search.focus(), 50);
    }
    function closePicker() {
        pickerEl.classList.remove('is-open');
        setTimeout(() => { pickerEl.hidden = true; }, 200);
        pickerTarget?.focus();
    }

    function enhanceIconInput(input) {
        if (input.dataset.ipReady) return;
        input.dataset.ipReady = '1';
        const wrap = document.createElement('div');
        wrap.className = 'ip-field';
        input.parentNode.insertBefore(wrap, input);
        const preview = document.createElement('button');
        preview.type = 'button';
        preview.className = 'ip-preview';
        preview.setAttribute('aria-label', 'Choose icon');
        const choose = document.createElement('button');
        choose.type = 'button';
        choose.className = 'btn btn-secondary btn-sm ip-choose';
        choose.innerHTML = '<i class="fas fa-icons"></i> Choose icon';
        wrap.append(preview, input, choose);
        const sync = () => { preview.innerHTML = '<i class="' + escapeHtml(input.value.trim() || 'fas fa-question') + '"></i>'; };
        input.addEventListener('input', sync);
        sync();
        preview.addEventListener('click', () => openPicker(input));
        choose.addEventListener('click', () => openPicker(input));
    }

    /* ---------- Slug + URL preview ---------- */
    const slugify = (v) => v.toString().normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase()
        .replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 190);

    function enhanceSlug(input) {
        const source = document.getElementById(input.dataset.slugFrom);
        if (!source) return;
        const preview = document.querySelector('[data-url-preview]');
        const categorySelect = document.getElementById('id_category');
        const categorySlugs = JSON.parse(document.getElementById('categorySlugs')?.textContent || '{}');
        const isNew = !input.value;
        let manual = !isNew;
        const original = input.value;

        const wrap = document.createElement('div');
        wrap.className = 'slug-field';
        input.parentNode.insertBefore(wrap, input);
        const lockBtn = document.createElement('button');
        lockBtn.type = 'button';
        lockBtn.className = 'btn btn-secondary btn-sm';
        wrap.append(input, lockBtn);
        const warn = document.createElement('p');
        warn.className = 'field-warning';
        warn.hidden = true;
        warn.innerHTML = '<i class="fas fa-triangle-exclamation"></i> Changing the address breaks links people may already have to this page (bookmarks, Google, emails).';
        wrap.after(warn);

        function render() {
            input.readOnly = !manual;
            lockBtn.innerHTML = manual ? '<i class="fas fa-rotate"></i> Auto' : '<i class="fas fa-pen"></i> Edit';
            lockBtn.title = manual ? 'Generate from the name again' : 'Type a custom address';
            warn.hidden = isNew || input.value === original;
            if (preview) {
                const base = preview.dataset.base || '/';
                let path = base;
                if (preview.dataset.kind === 'service') {
                    const cat = categorySlugs[categorySelect?.value] || 'category';
                    path = base + cat + '/';
                }
                preview.innerHTML = '<i class="fas fa-link"></i> ' + escapeHtml(location.host + path) + '<strong>' + escapeHtml(input.value || 'your-page') + '</strong>/';
            }
        }
        source.addEventListener('input', () => { if (!manual) { input.value = slugify(source.value); render(); } });
        input.addEventListener('input', () => { input.value = slugify(input.value); render(); });
        categorySelect?.addEventListener('change', render);
        lockBtn.addEventListener('click', () => {
            manual = !manual;
            if (!manual) input.value = slugify(source.value);
            render();
            if (manual) input.focus();
        });
        if (isNew && source.value) input.value = slugify(source.value);
        render();
    }

    /* ---------- Character counters ---------- */
    function enhanceCounter(el) {
        const ideal = parseInt(el.dataset.maxchars, 10);
        const out = document.createElement('span');
        out.className = 'char-counter';
        const labelRow = el.closest('.form-group')?.querySelector('.form-label-row');
        if (labelRow) labelRow.appendChild(out); else el.after(out);
        const sync = () => {
            const n = el.value.length;
            out.textContent = n + ' / ' + ideal;
            out.classList.toggle('is-over', n > ideal);
        };
        el.addEventListener('input', sync);
        sync();
    }

    /* ---------- Row repeaters (features, benefits, steps, FAQs) ---------- */
    function enhanceRepeater(root) {
        const hidden = document.querySelector('input[name="' + root.dataset.repeater + '"]');
        if (!hidden) return;
        const schema = JSON.parse(root.dataset.schema);
        const max = parseInt(root.dataset.max || '12', 10);
        const list = root.querySelector('.rp-list');
        const addBtn = root.querySelector('[data-rp-add]');
        const countEl = root.querySelector('[data-rp-count]');
        let rows = [];
        try { rows = JSON.parse(hidden.value || '[]'); } catch (e) { rows = []; }
        if (!Array.isArray(rows)) rows = [];

        function write() {
            const data = Array.from(list.children).map((row) => {
                const obj = {};
                schema.forEach((f) => { obj[f.key] = row.querySelector('[data-key="' + f.key + '"]').value.trim(); });
                return obj;
            });
            hidden.value = JSON.stringify(data);
            list.querySelectorAll('.rp-num').forEach((n, i) => { n.textContent = String(i + 1).padStart(2, '0'); });
            if (countEl) countEl.textContent = data.length;
            addBtn.disabled = data.length >= max;
            root.classList.toggle('is-empty', data.length === 0);
            root.dispatchEvent(new CustomEvent('rp:change', { bubbles: true }));
        }

        function rowHtml(data) {
            return '<div class="rp-row">' +
                '<div class="rp-side"><span class="rp-handle" title="Drag to reorder"><i class="fas fa-grip-vertical"></i></span><span class="rp-num"></span></div>' +
                '<div class="rp-fields">' + schema.map((f) => {
                    const val = escapeHtml(data[f.key] || '');
                    const id = 'rp' + Math.random().toString(36).slice(2, 9);
                    const field = f.type === 'textarea'
                        ? '<textarea class="form-control" rows="' + (f.rows || 2) + '" data-key="' + f.key + '" id="' + id + '" placeholder="' + escapeHtml(f.placeholder || '') + '" maxlength="600">' + val + '</textarea>'
                        : '<input class="form-control" type="text" data-key="' + f.key + '" id="' + id + '" value="' + val + '" placeholder="' + escapeHtml(f.placeholder || '') + '" maxlength="' + (f.max || 200) + '"' + (f.type === 'icon' ? ' data-icon-picker="1"' : '') + '>';
                    return '<div class="rp-field rp-field-' + (f.type || 'text') + '"><label for="' + id + '">' + escapeHtml(f.label) + '</label>' + field + '</div>';
                }).join('') + '</div>' +
                '<div class="rp-actions">' +
                    '<button type="button" class="rp-btn" data-rp-up title="Move up"><i class="fas fa-arrow-up"></i></button>' +
                    '<button type="button" class="rp-btn" data-rp-down title="Move down"><i class="fas fa-arrow-down"></i></button>' +
                    '<button type="button" class="rp-btn rp-btn-danger" data-rp-remove title="Remove"><i class="fas fa-trash"></i></button>' +
                '</div></div>';
        }

        function addRow(data, focus) {
            list.insertAdjacentHTML('beforeend', rowHtml(data || {}));
            const row = list.lastElementChild;
            row.querySelectorAll('[data-icon-picker]').forEach(enhanceIconInput);
            if (focus) row.querySelector('input:not([data-icon-picker]), textarea')?.focus();
            write();
        }

        rows.forEach((r) => addRow(r, false));
        addBtn.addEventListener('click', () => addRow({}, true));
        list.addEventListener('input', write);
        list.addEventListener('change', write);
        list.addEventListener('click', (e) => {
            const row = e.target.closest('.rp-row');
            if (!row) return;
            if (e.target.closest('[data-rp-remove]')) {
                const hasContent = Array.from(row.querySelectorAll('[data-key]')).some((el) => el.value.trim() && !el.dataset.iconPicker);
                if (!hasContent || confirm('Remove this item?')) { row.remove(); write(); }
            } else if (e.target.closest('[data-rp-up]') && row.previousElementSibling) {
                row.parentNode.insertBefore(row, row.previousElementSibling); write();
            } else if (e.target.closest('[data-rp-down]') && row.nextElementSibling) {
                row.parentNode.insertBefore(row.nextElementSibling, row); write();
            }
        });
        if (window.Sortable) {
            window.Sortable.create(list, { handle: '.rp-handle', animation: 200, ghostClass: 'rp-ghost', onEnd: write });
        }
        write();
    }

    /* ---------- Section nav (scroll-spy) ---------- */
    function enhanceSectionNav(nav) {
        const links = Array.from(nav.querySelectorAll('a[href^="#"]'));
        const sections = links.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);
        links.forEach((a) => a.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelector(a.getAttribute('href'))?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }));
        if (!('IntersectionObserver' in window)) return;
        const io = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) links.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === '#' + entry.target.id));
            });
        }, { rootMargin: '-20% 0px -70% 0px' });
        sections.forEach((s) => io.observe(s));
        // Flag sections that contain errors
        sections.forEach((s) => {
            if (s.querySelector('.form-error')) nav.querySelector('a[href="#' + s.id + '"]')?.classList.add('has-error');
        });
    }

    /* ---------- Unsaved-changes guard ---------- */
    function guardForm(form) {
        let dirty = false;
        form.addEventListener('input', () => { dirty = true; });
        form.addEventListener('change', () => { dirty = true; });
        form.addEventListener('submit', () => { dirty = false; });
        window.addEventListener('beforeunload', (e) => { if (dirty) { e.preventDefault(); e.returnValue = ''; } });
    }


    /* ---------- Image upload with preview ---------- */
    function enhanceImageInput(input) {
        const current = input.dataset.current || '';
        const zone = document.createElement('div');
        zone.className = 'img-drop';
        zone.innerHTML =
            '<div class="img-drop-preview"><img alt="" hidden><span class="img-drop-empty"><i class="fas fa-image"></i></span></div>' +
            '<div class="img-drop-body"><strong data-img-title>Upload an image</strong>' +
            '<span data-img-sub>Drag &amp; drop here, or click to browse. JPG, PNG or WebP, up to 5 MB.</span>' +
            '<button type="button" class="btn btn-secondary btn-sm" data-img-pick><i class="fas fa-upload"></i> <span>Choose image</span></button></div>';
        input.parentNode.insertBefore(zone, input);
        zone.appendChild(input);
        const img = zone.querySelector('img'), empty = zone.querySelector('.img-drop-empty');
        const title = zone.querySelector('[data-img-title]'), sub = zone.querySelector('[data-img-sub]');
        const pickLabel = zone.querySelector('[data-img-pick] span');
        function show(src, heading, detail) {
            img.src = src; img.hidden = false; empty.hidden = true;
            title.textContent = heading; sub.textContent = detail; pickLabel.textContent = 'Replace image';
            zone.classList.add('has-image');
        }
        if (current) show(current, 'Current image', current.split('/').pop());
        zone.querySelector('[data-img-pick]').addEventListener('click', () => input.click());
        zone.addEventListener('click', (e) => { if (e.target === zone || e.target.closest('.img-drop-preview')) input.click(); });
        input.addEventListener('change', () => {
            const file = input.files[0];
            if (!file) return;
            show(URL.createObjectURL(file), file.name, (file.size / 1024 / 1024).toFixed(2) + ' MB · will be uploaded when you save');
        });
        ['dragenter', 'dragover'].forEach((ev) => zone.addEventListener(ev, (e) => { e.preventDefault(); zone.classList.add('is-drag'); }));
        ['dragleave', 'drop'].forEach((ev) => zone.addEventListener(ev, (e) => { e.preventDefault(); zone.classList.remove('is-drag'); }));
        zone.addEventListener('drop', (e) => {
            if (!e.dataTransfer.files.length) return;
            input.files = e.dataTransfer.files;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        });
    }

    /* ---------- Live validation (green / red) ---------- */
    const ICON_RE = /^fa[srb]? fa-[a-z0-9-]+$/;
    const plural = (n, w) => n + ' ' + w + (n === 1 ? '' : 's');

    function richTextOf(el) {
        const editable = el.closest('.form-group')?.querySelector('.ck-editor__editable');
        if (editable) return editable.innerText.replace(/ /g, ' ').trim();
        const tmp = document.createElement('div');
        tmp.innerHTML = el.value;
        return tmp.textContent.trim();
    }

    function checkField(el) {
        const isFile = el.type === 'file';
        let value = isFile ? '' : (el.dataset.richtext ? richTextOf(el) : el.value.trim());
        if (el.dataset.required) {
            if (isFile) {
                if (!el.files.length && !el.dataset.current) return 'Please upload an image.';
                const f = el.files[0];
                if (f && f.size > 5 * 1024 * 1024) return 'This image is larger than 5 MB.';
                return '';
            }
            if (!value) return el.tagName === 'SELECT' ? 'Please choose an option.' : 'This field is required.';
        }
        if (el.dataset.iconPicker && value && !ICON_RE.test(value)) return 'Please choose an icon with "Choose icon".';
        const min = parseInt(el.dataset.minlen || '0', 10);
        if (min && value.length < min) return 'Write at least ' + min + ' characters (' + value.length + ' so far).';
        const max = parseInt(el.dataset.maxchars || '0', 10);
        if (max && value.length > max) return 'Keep this under ' + max + ' characters.';
        return '';
    }

    function checkRepeater(root) {
        const rows = Array.from(root.querySelectorAll('.rp-row'));
        const min = parseInt(root.dataset.min || '1', 10);
        const noun = root.dataset.noun || 'item';
        let incomplete = 0;
        rows.forEach((row) => {
            let rowBad = false;
            row.querySelectorAll('[data-key]').forEach((f) => {
                const bad = !f.value.trim() || (f.dataset.iconPicker && !ICON_RE.test(f.value.trim()));
                f.classList.toggle('is-invalid-input', bad && root.dataset.touched === '1');
                f.classList.toggle('is-valid-input', !bad);
                rowBad = rowBad || bad;
            });
            row.classList.toggle('is-incomplete', rowBad && root.dataset.touched === '1');
            if (rowBad) incomplete++;
        });
        if (rows.length < min) return 'Add at least ' + plural(min, noun) + ' (' + rows.length + ' so far).';
        if (incomplete) return plural(incomplete, noun) + ' ' + (incomplete === 1 ? 'is' : 'are') + ' missing text. Fill in every box.';
        return '';
    }

    function setState(group, message, touched) {
        if (!group) return;
        const err = group.querySelector(':scope > [data-live-error]');
        const valid = !message;
        group.classList.toggle('is-valid', valid && touched);
        group.classList.toggle('is-invalid', !valid && touched);
        group.classList.remove('has-error');
        if (err) {
            err.hidden = valid || !touched;
            const span = err.querySelector('span');
            if (span) span.textContent = message;
        }
    }

    function enhanceValidation(form) {
        const fields = Array.from(form.querySelectorAll('[data-required], [data-minlen], [data-maxchars]'))
            .filter((el) => el.closest('.form-group') && !el.closest('.rp'));
        const repeaters = Array.from(form.querySelectorAll('.rp'));
        const sections = Array.from(form.querySelectorAll('[data-section]'));
        const nav = form.querySelector('[data-section-nav]');
        const progress = document.querySelector('[data-progress]');
        const hint = form.querySelector('[data-savebar-hint]');
        const hintDefault = hint ? hint.innerHTML : '';
        const touched = new WeakSet();
        // Fields that arrive with server errors count as touched so the red shows immediately
        fields.forEach((el) => { if (el.closest('.form-group.has-error')) touched.add(el); });
        repeaters.forEach((r) => { if (r.classList.contains('has-error')) r.dataset.touched = '1'; });

        function run(force) {
            let firstInvalid = null, invalidCount = 0;
            const results = new Map();
            fields.forEach((el) => {
                if (force || (el.dataset.slugFrom && el.value)) touched.add(el);
                const msg = checkField(el);
                results.set(el, msg);
                setState(el.closest('.form-group'), msg, touched.has(el));
                if (msg) { invalidCount++; firstInvalid = firstInvalid || el; }
            });
            repeaters.forEach((r) => {
                if (force) r.dataset.touched = '1';
                const msg = checkRepeater(r);
                results.set(r, msg);
                setState(r, msg, r.dataset.touched === '1');
                if (msg) { invalidCount++; firstInvalid = firstInvalid || r; }
            });
            let done = 0;
            sections.forEach((sec) => {
                const members = [...fields, ...repeaters].filter((el) => sec.contains(el));
                const ok = members.every((el) => !results.get(el));
                const touchedBad = members.some((el) => results.get(el) && (touched.has(el) || el.dataset?.touched === '1'));
                const showBad = !ok && (touchedBad || force);
                sec.classList.toggle('is-complete', ok);
                sec.classList.toggle('is-incomplete', showBad);
                const link = nav?.querySelector('a[href="#' + sec.id + '"]');
                link?.classList.toggle('is-complete', ok);
                link?.classList.toggle('has-error', showBad);
                if (ok) done++;
            });
            if (progress) {
                const total = sections.length || 1;
                progress.querySelector('[data-progress-count]').textContent = done;
                progress.querySelector('[data-progress-total]').textContent = total;
                progress.style.setProperty('--p', (done / total).toFixed(3));
                progress.classList.toggle('is-done', done === total);
            }
            if (hint) {
                hint.innerHTML = invalidCount && force
                    ? '<i class="fas fa-circle-exclamation"></i> ' + plural(invalidCount, 'field') + ' still need' + (invalidCount === 1 ? 's' : '') + ' attention.'
                    : hintDefault;
                hint.classList.toggle('is-error', !!(invalidCount && force));
            }
            return { invalidCount, firstInvalid };
        }

        fields.forEach((el) => {
            const mark = () => { touched.add(el); run(false); };
            el.addEventListener('blur', mark);
            el.addEventListener('change', mark);
            el.addEventListener('input', () => { if (touched.has(el) || el.dataset.slugFrom || el.dataset.iconPicker) touched.add(el); run(false); });
            if (el.dataset.richtext) {
                const hook = () => {
                    const editable = el.closest('.form-group')?.querySelector('.ck-editor__editable');
                    if (!editable) return false;
                    editable.addEventListener('input', mark);
                    editable.addEventListener('keyup', mark);
                    editable.addEventListener('blur', mark, true);
                    new MutationObserver(() => { if (touched.has(el)) run(false); }).observe(editable, { childList: true, subtree: true, characterData: true });
                    return true;
                };
                if (!hook()) { const t = setInterval(() => { if (hook()) clearInterval(t); }, 250); setTimeout(() => clearInterval(t), 8000); }
            }
        });
        form.addEventListener('rp:change', (e) => { e.target.dataset.touched = e.target.dataset.touched || (e.target.querySelector('.rp-row') ? '0' : '0'); run(false); });
        form.addEventListener('focusout', (e) => {
            const r = e.target.closest('.rp');
            if (r) { r.dataset.touched = '1'; run(false); }
        });
        form.addEventListener('click', (e) => {
            if (e.target.closest('[data-rp-remove]')) {
                const r = e.target.closest('.rp'); if (r) { r.dataset.touched = '1'; setTimeout(() => run(false), 0); }
            }
        });

        form.addEventListener('submit', (e) => {
            if (e.submitter && e.submitter.form !== form) return;
            const { invalidCount, firstInvalid } = run(true);
            if (!invalidCount) return;
            e.preventDefault();
            e.stopImmediatePropagation();
            const target = firstInvalid.closest('.form-group, .rp') || firstInvalid;
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
            target.classList.remove('shake'); void target.offsetWidth; target.classList.add('shake');
            setTimeout(() => {
                const focusable = target.querySelector('input:not([type=hidden]):not([readonly]), textarea, select, .ck-editor__editable');
                focusable?.focus({ preventScroll: true });
            }, 400);
        }, true);

        run(false);
        setTimeout(() => run(false), 1200); // after CKEditor has rendered
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('input[data-icon-picker]').forEach(enhanceIconInput);
        document.querySelectorAll('input[data-slug-from]').forEach(enhanceSlug);
        document.querySelectorAll('[data-maxchars]').forEach(enhanceCounter);
        document.querySelectorAll('[data-repeater]').forEach(enhanceRepeater);
        document.querySelectorAll('[data-section-nav]').forEach(enhanceSectionNav);
        document.querySelectorAll('input[data-image-input]').forEach(enhanceImageInput);
        document.querySelectorAll('form[data-validate]').forEach(enhanceValidation);
        document.querySelectorAll('form[data-guard]').forEach(guardForm);
        // First field with an error gets focus
        document.querySelector('.form-group.has-error input, .form-group.has-error textarea, .form-group.has-error select')?.focus();
    });
})();
