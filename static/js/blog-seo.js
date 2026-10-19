/* Live SEO score for the blog editor. Mirrors insights/seo.py (keep the rules in sync). */
(function () {
    'use strict';
    const panel = document.getElementById('seoPanel');
    if (!panel) return;
    const $ = (id) => document.getElementById(id);
    const el = {
        title: $('id_title'), slug: $('id_slug'), kw: $('id_focus_keyword'), excerpt: $('id_excerpt'),
        meta: $('id_meta_description'), metaTitle: $('id_meta_title'), tags: $('id_tags'), cover: $('id_featured_image'), content: $('id_content'),
    };
    const norm = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().replace(/\s+/g, ' ');
    const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const getHtml = () => {
        const ed = window.editors && window.editors['id_content'];
        try { if (ed && ed.getData) return ed.getData(); } catch (e) { /* not ready */ }
        return el.content ? el.content.value : '';
    };
    const textOf = (html) => { const d = document.createElement('div'); d.innerHTML = html; return d.textContent || ''; };

    function report() {
        const title = (el.title?.value || '').trim();
        const kw = norm(el.kw?.value);
        const html = getHtml();
        const words = textOf(html).trim().split(/\s+/).filter(Boolean).length;
        const meta = (el.meta?.value || '').trim();
        const firstP = norm(textOf((html.match(/<p[^>]*>([\s\S]*?)<\/p>/i) || [, ''])[1]));
        const h2s = Array.from(html.matchAll(/<h2[^>]*>([\s\S]*?)<\/h2>/gi)).map((m) => norm(textOf(m[1])));
        const internal = /href="(\/|https?:\/\/(www\.)?tmsolutech\.com)/i.test(html);
        const tags = (el.tags?.value || '').split(',').filter((t) => t.trim());
        const slugWords = norm((el.slug?.value || '').replace(/-/g, ' '));
        const hasCover = !!(el.cover && el.cover.files && el.cover.files.length) || panel.dataset.hasCover === '1';
        const checks = [];
        const add = (ok, pts, label, tip, partial) => checks.push({ ok: ok === true, partial: ok === 'partial', points: ok === true ? pts : ok === 'partial' ? (partial || 0) : 0, max: pts, label, tip });
        const tl = title.length;
        add((tl >= 30 && tl <= 65) || (tl >= 20 && tl <= 75 ? 'partial' : false), 10, `Title length (${tl} characters)`, 'Aim for 30 to 65 characters so it fits in Google results.', 5);
        add(!!kw, 5, 'Focus keyword set', 'Add the main phrase people would search for.');
        add(!!kw && norm(title).includes(kw), 10, 'Keyword in title', 'Use the focus keyword in the title, ideally near the start.');
        add(!!kw && (firstP.includes(kw) || norm(el.excerpt?.value).includes(kw)), 5, 'Keyword in introduction', 'Mention the keyword in the summary or first paragraph.');
        add(!!kw && slugWords.includes(kw), 5, 'Keyword in web address', 'Include the keyword in the slug.');
        add(!!kw && norm(meta).includes(kw), 5, 'Keyword in search description', 'Include the keyword in the search description.');
        add(!!kw && h2s.some((h) => h.includes(kw)), 5, 'Keyword in a subheading', 'Use the keyword in at least one Heading 2.');
        const ml = meta.length;
        add((ml >= 120 && ml <= 160) || (ml ? 'partial' : false), 10, `Search description length (${ml} characters)`, 'Write 120 to 160 characters for the Google snippet.', 5);
        add(!!(el.excerpt?.value || '').trim(), 5, 'Summary written', 'A one or two sentence summary for cards and previews.');
        add(words >= 600 || (words >= 300 ? 'partial' : false), 15, `Content length (${words} words)`, '600+ words ranks best; 300 is the minimum.', 8);
        add(h2s.length >= 2, 5, `Subheadings (${h2s.length})`, 'Break the article up with at least two Heading 2 sections.');
        add(hasCover, 10, 'Cover image', 'Add a cover image for cards, the article and link previews.');
        add(internal, 5, 'Link to another page on the site', 'Link to a related service or article.');
        add(tags.length >= 2, 5, `Tags (${tags.length})`, 'Add at least two tags.');
        const score = checks.reduce((a, c) => a + c.points, 0);
        return { score, checks, title, meta };
    }

    let last = '';
    function render() {
        const r = report();
        const key = JSON.stringify([r.score, r.checks.map((c) => c.points + c.label)]);
        // Google preview always updates
        $('seoSlug').textContent = el.slug?.value || 'your-post';
        $('seoTitle').textContent = ((el.metaTitle?.value || '').trim() || r.title || 'Post title') + ' | TM Solutech';
        $('seoDesc').textContent = r.meta || (el.excerpt?.value || '').trim() || 'Add a search description so Google shows the right text.';
        if (key === last) return;
        last = key;
        const ring = $('seoRing');
        ring.style.setProperty('--p', r.score);
        ring.classList.toggle('is-good', r.score >= 80);
        ring.classList.toggle('is-ok', r.score >= 50 && r.score < 80);
        $('seoScore').textContent = r.score;
        $('seoGrade').textContent = r.score >= 80 ? 'Good' : r.score >= 50 ? 'Needs work' : 'Poor';
        const passed = r.checks.filter((c) => c.ok).length;
        $('seoPassed').textContent = `${passed} of ${r.checks.length} checks passed`;
        const sorted = r.checks.slice().sort((a, b) => (a.ok - b.ok) || (a.partial - b.partial));
        $('seoChecks').innerHTML = sorted.map((c) =>
            `<li class="${c.ok ? 'is-ok' : c.partial ? 'is-partial' : ''}"><i class="fas ${c.ok ? 'fa-check' : c.partial ? 'fa-minus' : 'fa-xmark'}"></i><span>${esc(c.label)}</span><b>${c.points}/${c.max}</b><small>${esc(c.tip)}</small></li>`
        ).join('');
    }
    let t = null;
    const schedule = () => { clearTimeout(t); t = setTimeout(render, 150); };
    document.querySelector('form.ed')?.addEventListener('input', schedule);
    document.querySelector('form.ed')?.addEventListener('change', schedule);
    // CKEditor content changes don't bubble as input events: poll lightly
    setInterval(render, 1200);
    render();
})();
