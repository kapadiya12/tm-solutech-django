/* Dashboard · Inquiries: quick view card, instant read/unread, bulk select, copy */
(function () {
    'use strict';
    const csrf = () => (document.querySelector('input[name="csrfmiddlewaretoken"]') || {}).value || '';
    const toast = document.getElementById('iqToast');
    let toastTimer = null;
    function flash(text) {
        if (!toast) return;
        toast.innerHTML = '<i class="fas fa-circle-check" aria-hidden="true"></i>' + text;
        toast.hidden = false;
        requestAnimationFrame(() => toast.classList.add('is-on'));
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => { toast.classList.remove('is-on'); setTimeout(() => { toast.hidden = true; }, 300); }, 1800);
    }

    async function setRead(url, read) {
        const body = new FormData();
        body.append('csrfmiddlewaretoken', csrf());
        body.append('read', read ? '1' : '0');
        const res = await fetch(url, { method: 'POST', body, headers: { 'X-Requested-With': 'fetch' }, credentials: 'same-origin' });
        if (!res.ok) throw new Error('failed');
        return res.json();
    }

    function updateUnreadBadges(unread) {
        const badge = document.querySelector('.sidebar-link .sidebar-badge');
        if (badge) { badge.textContent = unread; badge.hidden = unread === 0; }
        const tab = document.querySelector('.iq-tabs a:nth-child(2) span');
        if (tab) { tab.textContent = unread; tab.hidden = unread === 0; }
        const stat = document.querySelector('.iq-stat-unread strong');
        if (stat) stat.textContent = unread;
    }

    /* ---------------- List page ---------------- */
    const dataEl = document.getElementById('iqData');
    const items = dataEl ? JSON.parse(dataEl.textContent) : [];
    const byId = Object.fromEntries(items.map((it) => [String(it.id), it]));
    const rowOf = (id) => document.querySelector('.iq-row[data-id="' + id + '"]');

    function paintRow(id, read) {
        const row = rowOf(id);
        if (!row) return;
        row.classList.toggle('is-unread', !read);
        const btn = row.querySelector('[data-toggle-read] button');
        if (btn) {
            btn.title = btn.ariaLabel = read ? 'Mark as unread' : 'Mark as read';
            btn.innerHTML = '<i class="fas ' + (read ? 'fa-envelope' : 'fa-envelope-open') + '"></i>';
        }
        if (byId[id]) byId[id].is_read = read;
    }

    async function toggle(id, read) {
        const it = byId[id];
        if (!it) return;
        try {
            const data = await setRead(it.toggle, read);
            paintRow(id, data.is_read);
            updateUnreadBadges(data.unread);
            return data.is_read;
        } catch (e) { flash('Could not update. Please try again.'); return it.is_read; }
    }

    // Row read/unread buttons: no page reload
    document.querySelectorAll('[data-toggle-read]').forEach((form) => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = form.closest('.iq-row').dataset.id;
            const nowRead = await toggle(id, !byId[id].is_read);
            flash(nowRead ? 'Marked as read' : 'Marked as unread');
        });
    });

    /* Quick view */
    const modal = document.getElementById('iqModal');
    let current = -1;
    let lastFocus = null;
    const $ = (k) => modal.querySelector('[data-m="' + k + '"]');

    function render(index) {
        const it = items[index];
        if (!it) return;
        current = index;
        $('initial').textContent = (it.name || '?').charAt(0).toUpperCase();
        $('name').textContent = it.name;
        $('company').textContent = it.company || 'No company given';
        const st = $('status'); st.textContent = it.status_label; st.className = 'status-badge status-' + it.status;
        const em = $('email'); em.textContent = it.email; em.href = 'mailto:' + it.email;
        $('phone').innerHTML = it.phone ? '<a href="tel:' + it.phone.replace(/\s/g, '') + '">' + it.phone + '</a>' : 'Not provided';
        $('service').textContent = it.service || 'Not specified';
        $('date').textContent = it.date;
        $('message').textContent = it.message;
        modal.querySelector('[data-m-notes]').hidden = !it.notes;
        $('notes').textContent = it.notes;
        $('reply').href = 'mailto:' + it.email + '?subject=' + encodeURIComponent('Re: your enquiry to TM Solutech');
        $('open').href = it.url;
        modal.querySelector('[data-step="-1"]').disabled = index === 0;
        modal.querySelector('[data-step="1"]').disabled = index === items.length - 1;
        paintToggle(it.is_read);
        if (!it.is_read) toggle(String(it.id), true).then(paintToggle);  // opening = reading
    }
    function paintToggle(read) {
        const b = modal.querySelector('[data-m-toggle]');
        b.innerHTML = '<i class="fas ' + (read ? 'fa-envelope' : 'fa-envelope-open') + '"></i> <span>' + (read ? 'Mark as unread' : 'Mark as read') + '</span>';
    }
    function open(id) {
        const index = items.findIndex((it) => String(it.id) === String(id));
        if (index < 0) return;
        lastFocus = document.activeElement;
        modal.hidden = false;
        document.documentElement.style.overflow = 'hidden';
        render(index);
        modal.querySelector('.iq-modal-card').focus();
    }
    function close() {
        modal.hidden = true;
        document.documentElement.style.overflow = '';
        if (lastFocus) lastFocus.focus();
    }
    if (modal) {
        document.querySelectorAll('.iq-row').forEach((row) => {
            row.addEventListener('click', (e) => {
                if (e.target.closest('a, button, input, label, form')) return;
                open(row.dataset.id);
            });
            row.addEventListener('keydown', (e) => { if (e.key === 'Enter' && e.target === row) open(row.dataset.id); });
        });
        document.querySelectorAll('[data-quickview]').forEach((b) => b.addEventListener('click', () => open(b.dataset.quickview)));
        modal.querySelectorAll('[data-close]').forEach((b) => b.addEventListener('click', close));
        modal.querySelectorAll('[data-step]').forEach((b) => b.addEventListener('click', () => render(current + Number(b.dataset.step))));
        modal.querySelector('[data-m-toggle]').addEventListener('click', async () => {
            const it = items[current];
            const read = await toggle(String(it.id), !it.is_read);
            paintToggle(read);
            flash(read ? 'Marked as read' : 'Marked as unread');
        });
        document.addEventListener('keydown', (e) => {
            if (modal.hidden) return;
            if (e.key === 'Escape') close();
            else if (e.key === 'ArrowLeft' && current > 0) render(current - 1);
            else if (e.key === 'ArrowRight' && current < items.length - 1) render(current + 1);
        });
    }

    /* Bulk selection */
    const bulk = document.getElementById('iqBulk');
    if (bulk) {
        const boxes = Array.from(document.querySelectorAll('.iq-check input'));
        const all = document.querySelector('[data-select-all]');
        const sync = () => {
            const n = boxes.filter((b) => b.checked).length;
            bulk.hidden = n === 0;
            bulk.querySelector('[data-bulk-count]').textContent = n;
            boxes.forEach((b) => b.closest('.iq-row').classList.toggle('is-selected', b.checked));
            if (all) { all.checked = n && n === boxes.length; all.indeterminate = n > 0 && n < boxes.length; }
        };
        boxes.forEach((b) => b.addEventListener('change', sync));
        if (all) all.addEventListener('change', () => { boxes.forEach((b) => { b.checked = all.checked; }); sync(); });
        bulk.querySelector('[data-bulk-cancel]').addEventListener('click', () => { boxes.forEach((b) => { b.checked = false; }); sync(); });
    }

    /* Copy buttons (detail page) */
    document.querySelectorAll('[data-copy-text]').forEach((btn) => {
        btn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(btn.dataset.copyText);
                flash('Copied');
            } catch (e) { flash('Press Ctrl+C to copy'); }
        });
    });
})();
