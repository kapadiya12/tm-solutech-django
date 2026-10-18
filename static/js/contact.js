/* Contact page: live validation (mirrors contact/forms.py), in-page submit,
   success state, draft autosave, copy-to-clipboard, office open/closed status. */
(function () {
    'use strict';
    const form = document.getElementById('contactForm');
    if (!form) return;

    const MIN = parseInt(form.dataset.messageMin, 10) || 20;
    const MAX = parseInt(form.dataset.messageMax, 10) || 2000;
    const NAME_RE = /^\p{L}+(?:(?:\. ?|[ '\-])\p{L}+)*\.?$/u;
    const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    const URL_RE = /(https?:\/\/|www\.)/gi;
    const DRAFT_KEY = 'tmContactDraft';
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const card = document.getElementById('contactFormCard');
    const alertBox = document.getElementById('cfAlert');
    const alertText = document.getElementById('cfAlertText');
    const submit = document.getElementById('cfSubmit');
    const success = document.getElementById('cfSuccess');
    const successText = document.getElementById('cfSuccessText');
    const tokenInput = form.querySelector('input[name="form_token"]');
    const message = form.querySelector('#id_message');
    const counter = form.querySelector('#cf_counter [data-count]');
    const counterWrap = form.querySelector('#cf_counter');

    const squash = (v) => v.replace(/\s+/g, ' ').trim();

    const rules = {
        name(v) {
            v = squash(v);
            if (!v) return 'Please enter your full name.';
            if (v.length < 2) return 'Your name looks too short.';
            if (v.length > 100) return 'Please keep your name under 100 characters.';
            if (!NAME_RE.test(v)) return 'Use letters only. Spaces, dots, hyphens and apostrophes are fine.';
            return '';
        },
        company(v) {
            v = squash(v);
            if (!v) return 'Please enter your company name.';
            if (v.length < 2) return 'Your company name looks too short.';
            if (v.length > 150) return 'Please keep the company name under 150 characters.';
            if (/(https?:\/\/|www\.)/i.test(v)) return 'Please enter the company name, not a link.';
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
            if (!/^\+?[\d\s\-()]+$/.test(v)) return 'Use digits only. A leading + and spaces are fine.';
            const digits = v.replace(/\D/g, '').length;
            if (digits < 10 || digits > 15) return 'Please enter a 10 to 15 digit phone number.';
            return '';
        },
        message(v) {
            v = v.trim();
            if (!v) return 'Please tell us a little about what you need.';
            if (v.length < MIN) return `Please add a little more detail (at least ${MIN} characters).`;
            if (v.length > MAX) return `Please keep your message under ${MAX} characters.`;
            if ((v.match(URL_RE) || []).length > 3) return 'Please remove some links. Messages with many links are blocked as spam.';
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
        const optionalEmpty = name === 'phone' && !el.value.trim();
        box.classList.toggle('is-valid', !msg && name !== 'consent' && el.value.trim() !== '' && !optionalEmpty);
        if (msg) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid');
    }

    function check(name) {
        const el = control(name);
        if (!el || !rules[name]) return '';
        const msg = rules[name](el.value || '', el);
        setError(name, msg);
        return msg;
    }

    // Validate on blur; once touched, re-validate as the user types
    const touched = new Set();
    Object.keys(rules).forEach((name) => {
        const el = control(name);
        if (!el) return;
        const evt = el.type === 'checkbox' ? 'change' : 'blur';
        el.addEventListener(evt, () => { touched.add(name); check(name); });
        el.addEventListener('input', () => {
            if (touched.has(name)) check(name);
            saveDraft();
        });
    });
    // Tidy whitespace when leaving name/company/email
    ['name', 'company', 'email'].forEach((name) => {
        const el = control(name);
        if (el) el.addEventListener('blur', () => { el.value = name === 'email' ? el.value.trim() : squash(el.value); });
    });

    // Live character counter
    function updateCounter() {
        if (!message || !counter) return;
        const n = message.value.trim().length;
        counter.textContent = message.value.length;
        counterWrap.classList.toggle('is-low', n > 0 && n < MIN);
        counterWrap.classList.toggle('is-ok', n >= MIN);
    }
    if (message) { message.addEventListener('input', updateCounter); updateCounter(); }

    // Draft autosave (per browser; cleared on success)
    const draftFields = ['name', 'company', 'email', 'phone', 'message', 'service'];
    function saveDraft() {
        try {
            const data = {};
            draftFields.forEach((n) => { const el = control(n); if (el) data[n] = el.value; });
            const topic = form.querySelector('[name="topic"]:checked');
            if (topic) data.topic = topic.value;
            localStorage.setItem(DRAFT_KEY, JSON.stringify(data));
        } catch (e) { /* storage unavailable */ }
    }
    function restoreDraft() {
        let data = null;
        try { data = JSON.parse(localStorage.getItem(DRAFT_KEY) || 'null'); } catch (e) { data = null; }
        if (!data) return;
        draftFields.forEach((n) => {
            const el = control(n);
            if (el && !el.value && data[n]) el.value = data[n];
        });
        if (data.topic) {
            const radio = form.querySelector(`[name="topic"][value="${CSS.escape(data.topic)}"]`);
            if (radio) radio.checked = true;
        }
        updateCounter();
    }
    function clearDraft() { try { localStorage.removeItem(DRAFT_KEY); } catch (e) { /* ignore */ } }
    const hasServerErrors = !!form.querySelector('.is-invalid');
    if (!hasServerErrors) restoreDraft();
    form.querySelectorAll('[name="topic"], [name="service"]').forEach((el) => el.addEventListener('change', saveDraft));

    function showAlert(text) {
        if (!alertBox) return;
        alertText.textContent = text || '';
        alertBox.hidden = false;
    }
    function hideAlert() { if (alertBox) alertBox.hidden = true; }

    function shake(box) {
        if (reduceMotion || !box) return;
        box.classList.remove('shake');
        void box.offsetWidth;
        box.classList.add('shake');
    }

    function validateAll() {
        const invalid = [];
        Object.keys(rules).forEach((name) => {
            touched.add(name);
            if (check(name)) invalid.push(name);
        });
        return invalid;
    }

    function setLoading(on) {
        submit.classList.toggle('is-loading', on);
        submit.disabled = on;
        submit.querySelector('.cf-submit-label').textContent = on ? 'Sending…' : 'Send message';
    }

    function showSuccess(text) {
        clearDraft();
        form.hidden = true;
        if (successText && text) successText.textContent = text;
        success.hidden = false;
        success.focus({ preventScroll: true });
        const top = card.getBoundingClientRect().top + window.scrollY - ((document.querySelector('.navbar') || {}).offsetHeight || 0) - 24;
        if (window.tmLenis) window.tmLenis.scrollTo(Math.max(top, 0), { duration: 0.9 });
        else window.scrollTo({ top: Math.max(top, 0), behavior: reduceMotion ? 'auto' : 'smooth' });
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        hideAlert();
        const invalid = validateAll();
        if (invalid.length) {
            showAlert(invalid.length === 1 ? '1 field needs your attention.' : `${invalid.length} fields need your attention.`);
            invalid.forEach((n) => shake(fieldBox(n)));
            const first = control(invalid[0]);
            if (first) first.focus();
            return;
        }
        if (!window.fetch || !window.FormData) { form.submit(); return; }

        setLoading(true);
        try {
            const res = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: { 'X-Requested-With': 'fetch' },
                credentials: 'same-origin',
            });
            const data = await res.json().catch(() => null);
            if (data && data.form_token && tokenInput) tokenInput.value = data.form_token;
            if (res.ok && data && data.ok) {
                showSuccess(data.message);
            } else if (data && data.errors) {
                const general = (data.errors.__all__ || []).join(' ');
                const fieldNames = Object.keys(data.errors).filter((k) => k !== '__all__');
                fieldNames.forEach((name) => { setError(name, data.errors[name][0]); shake(fieldBox(name)); });
                showAlert(general || (fieldNames.length ? 'Please fix the highlighted fields.' : 'Something went wrong. Please try again.'));
                const first = fieldNames.length && control(fieldNames[0]);
                if (first) first.focus();
            } else {
                showAlert('Something went wrong on our side. Please try again, or email us directly.');
            }
        } catch (e) {
            showAlert('We could not reach the server. Check your connection and try again.');
        } finally {
            setLoading(false);
        }
    });

    const again = document.getElementById('cfAgain');
    if (again) {
        again.addEventListener('click', () => {
            const keepTopic = form.querySelector('[name="topic"]:checked');
            form.reset();
            if (keepTopic) keepTopic.checked = true;
            form.querySelectorAll('.is-valid, .is-invalid').forEach((el) => el.classList.remove('is-valid', 'is-invalid'));
            form.querySelectorAll('.cf-error').forEach((el) => { el.textContent = ''; });
            touched.clear();
            updateCounter();
            success.hidden = true;
            form.hidden = false;
            const first = control('name');
            if (first) first.focus();
        });
    }

    // Copy phone / email
    const toast = document.getElementById('cfToast');
    let toastTimer = null;
    function flash(text) {
        if (!toast) return;
        toast.innerHTML = '<i class="fas fa-circle-check" aria-hidden="true"></i>' + text;
        toast.hidden = false;
        requestAnimationFrame(() => toast.classList.add('is-on'));
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => { toast.classList.remove('is-on'); setTimeout(() => { toast.hidden = true; }, 300); }, 1800);
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
                flash('Copied ' + value);
                setTimeout(() => { btn.classList.remove('is-copied'); btn.innerHTML = '<i class="far fa-copy"></i>'; }, 1600);
            } catch (e) { flash('Press Ctrl+C to copy'); }
        });
    });

    // Office open / closed (Mon–Sat 9:30–18:30, India time)
    const pill = document.querySelector('[data-office-status]');
    if (pill && window.Intl) {
        const update = () => {
            const parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Kolkata', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
            const get = (t) => (parts.find((p) => p.type === t) || {}).value;
            const mins = parseInt(get('hour'), 10) * 60 + parseInt(get('minute'), 10);
            const open = get('weekday') !== 'Sun' && mins >= 570 && mins < 1110;
            pill.textContent = open ? 'Open now' : 'Closed now';
            pill.classList.toggle('is-open', open);
            pill.classList.toggle('is-closed', !open);
            pill.hidden = false;
        };
        update();
        setInterval(update, 60000);
    }
})();
