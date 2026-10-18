/* Dashboard UI kit: toasts · danger confirm dialog · styled dropdowns
   Loaded on every dashboard page (templates/dashboard/base.html). */
(function () {
    'use strict';
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const fold = (s) => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

    /* =====================================================================
       TOASTS
       ===================================================================== */
    const stack = document.getElementById('duiToasts') || (() => {
        const d = document.createElement('div'); d.className = 'dui-toasts'; d.id = 'duiToasts'; document.body.appendChild(d); return d;
    })();
    function arm(toast) {
        const ms = toast.classList.contains('dui-toast-error') ? 7000 : 4500;
        const bar = toast.querySelector('.dui-toast-bar');
        let left = ms, started = performance.now(), timer = null;
        const close = () => {
            toast.classList.add('is-leaving');
            setTimeout(() => toast.remove(), reduceMotion ? 0 : 280);
        };
        const run = () => {
            started = performance.now();
            timer = setTimeout(close, left);
            if (bar) { bar.style.transition = 'transform ' + left + 'ms linear'; bar.style.transform = 'scaleX(0)'; }
        };
        const pause = () => {
            clearTimeout(timer);
            left -= performance.now() - started;
            if (bar) { const k = Math.max(left / ms, 0); bar.style.transition = 'none'; bar.style.transform = 'scaleX(' + k + ')'; }
        };
        toast.addEventListener('mouseenter', pause);
        toast.addEventListener('mouseleave', run);
        toast.querySelector('.dui-toast-close')?.addEventListener('click', close);
        requestAnimationFrame(() => { toast.classList.add('is-in'); run(); });
    }
    stack.querySelectorAll('.dui-toast').forEach(arm);
    window.duiToast = function (text, tone) {
        tone = tone || 'success';
        const icon = { success: 'fa-circle-check', error: 'fa-circle-exclamation', warning: 'fa-triangle-exclamation', info: 'fa-circle-info' }[tone];
        const t = document.createElement('div');
        t.className = 'dui-toast dui-toast-' + tone;
        t.setAttribute('role', tone === 'error' ? 'alert' : 'status');
        t.innerHTML = '<span class="dui-toast-icon"><i class="fas ' + icon + '"></i></span><p>' + esc(text) + '</p><button type="button" class="dui-toast-close" aria-label="Dismiss"><i class="fas fa-xmark"></i></button><span class="dui-toast-bar"></span>';
        stack.appendChild(t);
        arm(t);
    };

    /* =====================================================================
       DANGER CONFIRM DIALOG
       Any form with data-confirm (or a submit button with data-confirm)
       Optional: data-confirm-title, data-confirm-name, data-confirm-action, data-confirm-bulk
       ===================================================================== */
    const dlg = document.createElement('div');
    dlg.className = 'dui-confirm';
    dlg.hidden = true;
    dlg.innerHTML =
        '<div class="dui-confirm-backdrop" data-cancel></div>' +
        '<div class="dui-confirm-card" role="alertdialog" aria-modal="true" aria-labelledby="duiConfirmTitle" aria-describedby="duiConfirmText">' +
            '<button type="button" class="dui-confirm-x" data-cancel aria-label="Cancel"><i class="fas fa-xmark"></i></button>' +
            '<span class="dui-confirm-icon" aria-hidden="true"><i class="fas fa-trash-can"></i></span>' +
            '<h3 id="duiConfirmTitle"></h3>' +
            '<div class="dui-confirm-name" hidden><i class="fas fa-file-lines" aria-hidden="true"></i><span></span></div>' +
            '<p id="duiConfirmText"></p>' +
            '<div class="dui-confirm-warn"><i class="fas fa-triangle-exclamation" aria-hidden="true"></i><span><strong>This cannot be undone.</strong> It is removed from the website and the dashboard straight away.</span></div>' +
            '<label class="dui-confirm-check"><input type="checkbox"><span class="dui-confirm-box" aria-hidden="true"><i class="fas fa-check"></i></span><span class="dui-confirm-ack">I understand this is permanent</span></label>' +
            '<div class="dui-confirm-actions">' +
                '<button type="button" class="dui-btn dui-btn-ghost" data-cancel>Cancel</button>' +
                '<button type="button" class="dui-btn dui-btn-danger" data-ok disabled><i class="fas fa-trash-can"></i> <span>Delete</span></button>' +
            '</div>' +
        '</div>';
    document.body.appendChild(dlg);
    const dTitle = dlg.querySelector('h3');
    const dText = dlg.querySelector('#duiConfirmText');
    const dName = dlg.querySelector('.dui-confirm-name');
    const dCheck = dlg.querySelector('.dui-confirm-check input');
    const dAck = dlg.querySelector('.dui-confirm-ack');
    const dOk = dlg.querySelector('[data-ok]');
    let pending = null;
    let lastFocus = null;

    function guessName(el) {
        const holder = el.closest('tr, .iq-row, .sl-row, li, .dashboard-card');
        if (!holder) return '';
        const strong = holder.querySelector('strong, .iq-name, td:nth-child(2)');
        return strong ? strong.textContent.trim().replace(/\s+/g, ' ').slice(0, 80) : '';
    }

    function openConfirm(form, submitter, source) {
        const action = source.dataset.confirmAction || 'Delete';
        let title = source.dataset.confirmTitle;
        let name = source.dataset.confirmName || guessName(source.tagName === 'FORM' ? source : submitter || form);
        if ('confirmBulk' in source.dataset) {
            const n = document.querySelectorAll('input[name="ids"][form="' + form.id + '"]:checked, #' + form.id + ' input[name="ids"]:checked').length;
            name = n + ' selected item' + (n === 1 ? '' : 's');
        }
        if (!title) title = /^(delete|remove)/i.test(source.dataset.confirm) ? source.dataset.confirm : action + ' permanently?';
        dTitle.textContent = title;
        const text = source.dataset.confirm;
        dText.textContent = text && text !== title && !/^delete this .*\?$/i.test(text) ? text : '';
        dText.hidden = !dText.textContent;
        dName.hidden = !name;
        dName.querySelector('span').textContent = name;
        dAck.textContent = 'I understand ' + (name ? '“' + name + '”' : 'this') + ' will be ' + (action.toLowerCase() === 'remove' ? 'removed' : 'permanently deleted');
        dOk.querySelector('span').textContent = action;
        dCheck.checked = false;
        dOk.disabled = true;
        dOk.classList.remove('is-busy');
        pending = { form, submitter };
        lastFocus = document.activeElement;
        dlg.hidden = false;
        document.documentElement.classList.add('dui-locked');
        requestAnimationFrame(() => dlg.classList.add('is-open'));
        setTimeout(() => dCheck.focus(), 60);
    }
    function closeConfirm() {
        dlg.classList.remove('is-open');
        document.documentElement.classList.remove('dui-locked');
        setTimeout(() => { dlg.hidden = true; }, reduceMotion ? 0 : 200);
        pending = null;
        if (lastFocus) lastFocus.focus();
    }
    dCheck.addEventListener('change', () => { dOk.disabled = !dCheck.checked; });
    dlg.querySelectorAll('[data-cancel]').forEach((b) => b.addEventListener('click', closeConfirm));
    dOk.addEventListener('click', () => {
        if (!pending || !dCheck.checked) return;
        const { form, submitter } = pending;
        dOk.classList.add('is-busy');
        dOk.disabled = true;
        form._duiConfirmed = true;
        if (submitter && submitter.name) {   // keep the clicked button's name/value (e.g. action=delete)
            const h = document.createElement('input');
            h.type = 'hidden'; h.name = submitter.name; h.value = submitter.value;
            form.appendChild(h);
        }
        HTMLFormElement.prototype.submit.call(form);
    });
    dlg.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') { e.preventDefault(); closeConfirm(); }
        if (e.key === 'Tab') {   // keep focus inside
            const f = Array.from(dlg.querySelectorAll('button:not([disabled]), input')).filter((el) => el.offsetParent !== null);
            if (!f.length) return;
            if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
            else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
        }
    });
    document.addEventListener('submit', (e) => {
        const form = e.target;
        if (form._duiConfirmed) return;
        const submitter = e.submitter || null;
        const source = form.hasAttribute('data-confirm') ? form : (submitter && submitter.hasAttribute('data-confirm') ? submitter : null);
        if (!source) return;
        e.preventDefault();
        e.stopImmediatePropagation();
        openConfirm(form, submitter, source);
    }, true);

    /* =====================================================================
       STYLED DROPDOWNS (enhances every single <select> in the dashboard)
       The native select stays in the form; change events still fire.
       ===================================================================== */
    let openMenu = null;
    document.addEventListener('pointerdown', (e) => { if (openMenu && !openMenu.root.contains(e.target) && !openMenu.menu.contains(e.target)) openMenu.close(); });
    window.addEventListener('resize', () => openMenu && openMenu.close());
    document.addEventListener('scroll', (e) => { if (openMenu && !openMenu.menu.contains(e.target)) openMenu.place(); }, true);

    function enhanceSelect(select) {
        if (select.multiple || select.dataset.native !== undefined || select.closest('.dui-select')) return;
        const root = document.createElement('div');
        root.className = 'dui-select' + (select.classList.contains('form-control') ? '' : ' dui-select-compact');
        select.parentNode.insertBefore(root, select);
        root.appendChild(select);
        select.classList.add('dui-native');
        select.tabIndex = -1;
        select.setAttribute('aria-hidden', 'true');

        const trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'dui-trigger ' + Array.from(select.classList).filter((c) => c !== 'dui-native').join(' ');
        trigger.setAttribute('aria-haspopup', 'listbox');
        trigger.setAttribute('aria-expanded', 'false');
        const label = select.id && document.querySelector('label[for="' + select.id + '"]');
        if (label) { label.id = label.id || select.id + '_lbl'; trigger.setAttribute('aria-labelledby', label.id + ' ' + select.id + '_val'); }
        else if (select.getAttribute('aria-label')) trigger.setAttribute('aria-label', select.getAttribute('aria-label'));
        trigger.innerHTML = '<span class="dui-value" id="' + (select.id || '') + '_val"></span><i class="fas fa-chevron-down dui-caret" aria-hidden="true"></i>';
        root.appendChild(trigger);
        if (select.id && label) label.addEventListener('click', (e) => { e.preventDefault(); trigger.focus(); });

        const menu = document.createElement('div');
        menu.className = 'dui-menu';
        menu.setAttribute('data-lenis-prevent', '');
        menu.innerHTML = '<div class="dui-search" hidden><i class="fas fa-magnifying-glass" aria-hidden="true"></i><input type="text" placeholder="Search…" aria-label="Search options"><button type="button" class="dui-clear" hidden aria-label="Clear"><i class="fas fa-xmark"></i></button></div><ul class="dui-list" role="listbox"></ul><p class="dui-empty" hidden>No matches</p>';
        document.body.appendChild(menu);
        const search = menu.querySelector('input');
        const clear = menu.querySelector('.dui-clear');
        const list = menu.querySelector('.dui-list');
        const empty = menu.querySelector('.dui-empty');
        let items = [], visible = [], active = -1;

        const sync = () => {
            const opt = select.options[select.selectedIndex];
            const text = opt ? opt.textContent.trim() : '';
            trigger.querySelector('.dui-value').textContent = text || '—';
            trigger.classList.toggle('is-placeholder', !select.value);
            trigger.disabled = select.disabled;
        };
        const read = () => {
            items = [];
            Array.from(select.options).forEach((o) => {
                const group = o.parentElement.tagName === 'OPTGROUP' ? o.parentElement.label : '';
                items.push({ value: o.value, label: o.textContent.trim(), group, disabled: o.disabled, search: fold(o.textContent + ' ' + group) });
            });
        };
        const render = (q) => {
            const query = fold((q || '').trim());
            visible = items.filter((it) => !query || it.search.includes(query));
            let html = '', lastGroup = null;
            visible.forEach((it, i) => {
                if (it.group && it.group !== lastGroup && !query) { lastGroup = it.group; html += '<li class="dui-group" role="presentation">' + esc(it.group) + '</li>'; }
                const sel = it.value === select.value;
                html += '<li class="dui-opt' + (sel ? ' is-selected' : '') + (it.disabled ? ' is-disabled' : '') + '" role="option" aria-selected="' + sel + '" data-i="' + i + '">' +
                        '<span>' + esc(it.label || '—') + '</span>' + (sel ? '<i class="fas fa-check" aria-hidden="true"></i>' : '') + '</li>';
            });
            list.innerHTML = html;
            empty.hidden = visible.length > 0;
            clear.hidden = !q;
            const s = visible.findIndex((it) => it.value === select.value);
            setActive(s >= 0 && !query ? s : 0, true);
        };
        const setActive = (i, center) => {
            const opts = list.querySelectorAll('.dui-opt');
            if (!opts.length) { active = -1; return; }
            active = Math.max(0, Math.min(i, opts.length - 1));
            opts.forEach((o, k) => o.classList.toggle('is-active', k === active));
            const el = opts[active];
            if (center) list.scrollTop = el.offsetTop - list.clientHeight / 2 + el.offsetHeight / 2;
            else if (el.offsetTop < list.scrollTop) list.scrollTop = el.offsetTop - 4;
            else if (el.offsetTop + el.offsetHeight > list.scrollTop + list.clientHeight) list.scrollTop = el.offsetTop + el.offsetHeight - list.clientHeight + 4;
        };
        const place = () => {
            const r = trigger.getBoundingClientRect();
            const w = Math.max(r.width, 200);
            menu.style.width = w + 'px';
            menu.style.left = Math.min(Math.max(8, r.left), window.innerWidth - w - 8) + 'px';
            const below = window.innerHeight - r.bottom;
            const up = below < 280 && r.top > below;
            menu.classList.toggle('is-up', up);
            menu.style.top = up ? '' : (r.bottom + 6) + 'px';
            menu.style.bottom = up ? (window.innerHeight - r.top + 6) + 'px' : '';
        };
        const pick = (it) => {
            if (!it || it.disabled) return;
            const changed = select.value !== it.value;
            select.value = it.value;
            sync();
            api.close();
            if (changed) {
                select.dispatchEvent(new Event('input', { bubbles: true }));
                select.dispatchEvent(new Event('change', { bubbles: true }));
            }
        };
        const api = {
            root, menu, place,
            open() {
                if (openMenu && openMenu !== api) openMenu.close();
                openMenu = api;
                read();
                const searchable = items.length > 8;
                menu.querySelector('.dui-search').hidden = !searchable;
                search.value = '';
                render('');
                place();
                menu.classList.add('is-open');
                root.classList.add('is-open');
                trigger.setAttribute('aria-expanded', 'true');
                if (searchable) setTimeout(() => search.focus({ preventScroll: true }), 30);
            },
            close(refocus) {
                if (openMenu !== api) return;
                openMenu = null;
                menu.classList.remove('is-open');
                root.classList.remove('is-open');
                trigger.setAttribute('aria-expanded', 'false');
                if (refocus) trigger.focus();
            },
        };
        trigger.addEventListener('click', () => (openMenu === api ? api.close() : api.open()));
        const keys = (e) => {
            if (openMenu !== api) {
                if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(e.key)) { e.preventDefault(); api.open(); }
                return;
            }
            if (e.key === 'ArrowDown') { e.preventDefault(); setActive(active + 1); }
            else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
            else if (e.key === 'Enter') { e.preventDefault(); pick(visible[active]); trigger.focus(); }
            else if (e.key === 'Escape') { e.preventDefault(); api.close(true); }
            else if (e.key === 'Tab') api.close();
            else if (e.target === trigger && e.key.length === 1) {   // type-ahead
                const i = visible.findIndex((it) => fold(it.label).startsWith(fold(e.key)));
                if (i >= 0) setActive(i, true);
            }
        };
        trigger.addEventListener('keydown', keys);
        search.addEventListener('keydown', keys);
        search.addEventListener('input', () => render(search.value));
        clear.addEventListener('click', () => { search.value = ''; render(''); search.focus(); });
        list.addEventListener('mousemove', (e) => { const li = e.target.closest('.dui-opt'); if (li && +li.dataset.i !== active) setActive(+li.dataset.i); });
        list.addEventListener('click', (e) => { const li = e.target.closest('.dui-opt'); if (li) { pick(visible[+li.dataset.i]); trigger.focus(); } });
        select.addEventListener('change', sync);
        select.form && select.form.addEventListener('reset', () => setTimeout(sync));
        sync();
        // Labels can be rewritten after load (e.g. country names); refresh once things settle
        requestAnimationFrame(sync);
        window.addEventListener('load', sync);
    }

    function enhanceAll(scope) {
        (scope || document).querySelectorAll('.dashboard-content select, .dashboard-topbar select').forEach(enhanceSelect);
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => enhanceAll());
    else enhanceAll();
    window.duiEnhanceSelects = enhanceAll;
})();
