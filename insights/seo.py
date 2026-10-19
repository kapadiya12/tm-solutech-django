"""SEO score for blog posts (0-100). The editor's live score (static/js/blog-seo.js) mirrors these rules."""
import re

from django.utils.html import strip_tags

GRADES = [(80, 'good', 'Good'), (50, 'ok', 'Needs work'), (0, 'poor', 'Poor')]


def _norm(s):
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).split())


def seo_report(post):
    title = (post.title or '').strip()
    kw = _norm(getattr(post, 'focus_keyword', ''))
    html = post.content or ''
    text = strip_tags(html)
    words = len(text.split())
    meta = (post.meta_description or '').strip()
    first_para = _norm(strip_tags((re.search(r'<p[^>]*>(.*?)</p>', html, re.S | re.I) or [None, ''])[1]))
    h2s = [_norm(strip_tags(h)) for h in re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.S | re.I)]
    internal = bool(re.search(r'href="(/|https?://(www\.)?tmsolutech\.com)', html, re.I))
    tags = [t for t in (post.tags or '').split(',') if t.strip()]
    slug_words = _norm((post.slug or '').replace('-', ' '))

    checks = []

    def add(ok, pts, label, tip, partial=0):
        got = pts if ok is True else (partial if ok == 'partial' else 0)
        checks.append({'ok': ok is True, 'partial': ok == 'partial', 'points': got, 'max': pts, 'label': label, 'tip': tip})

    tl = len(title)
    add(30 <= tl <= 65 or ('partial' if 20 <= tl <= 75 else False), 10, f'Title length ({tl} characters)', 'Aim for 30 to 65 characters so it fits in Google results.', 5)
    add(bool(kw), 5, 'Focus keyword set', 'Add the main phrase people would search for.')
    add(bool(kw) and kw in _norm(title), 10, 'Keyword in title', 'Use the focus keyword in the title, ideally near the start.')
    add(bool(kw) and (kw in first_para or kw in _norm(post.excerpt)), 5, 'Keyword in introduction', 'Mention the keyword in the summary or first paragraph.')
    add(bool(kw) and kw in slug_words, 5, 'Keyword in web address', 'Include the keyword in the slug.')
    add(bool(kw) and kw in _norm(meta), 5, 'Keyword in search description', 'Include the keyword in the search description.')
    add(bool(kw) and any(kw in h for h in h2s), 5, 'Keyword in a subheading', 'Use the keyword in at least one Heading 2.')
    ml = len(meta)
    add(120 <= ml <= 160 or ('partial' if ml else False), 10, f'Search description length ({ml} characters)', 'Write 120 to 160 characters for the Google snippet.', 5)
    add(bool((post.excerpt or '').strip()), 5, 'Summary written', 'A one or two sentence summary for cards and previews.')
    add(words >= 600 or ('partial' if words >= 300 else False), 15, f'Content length ({words} words)', '600+ words ranks best; 300 is the minimum.', 8)
    add(len(h2s) >= 2, 5, f'Subheadings ({len(h2s)})', 'Break the article up with at least two Heading 2 sections.')
    add(bool(post.featured_image), 10, 'Cover image', 'Add a cover image for cards, the article and link previews.')
    add(internal, 5, 'Link to another page on the site', 'Link to a related service or article.')
    add(len(tags) >= 2, 5, f'Tags ({len(tags)})', 'Add at least two tags.')

    score = sum(c['points'] for c in checks)
    grade = next(g for g in GRADES if score >= g[0])
    checks.sort(key=lambda c: (c['ok'], c['partial']))
    return {'score': score, 'grade': grade[1], 'grade_label': grade[2], 'checks': checks,
            'passed': sum(1 for c in checks if c['ok']), 'total': len(checks)}
