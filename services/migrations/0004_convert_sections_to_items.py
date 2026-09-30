import html
import json
import re

from django.db import migrations


def _text(fragment):
    return html.unescape(re.sub(r'<[^>]+>', '', fragment or '')).strip()


FEATURE_RE = re.compile(r'<div class="feat-box">.*?<i class="([^"]*)"></i>.*?<h4>(.*?)</h4>\s*<p>(.*?)</p>', re.S)
BENEFIT_RE = re.compile(r'<div class="benefit-item">.*?<strong>(.*?)</strong>(.*?)</div>\s*</div>', re.S)
PROCESS_RE = re.compile(r'<div class="proc-step">.*?<h4>(.*?)</h4>\s*<p>(.*?)</p>', re.S)


def convert(apps, schema_editor):
    Service = apps.get_model('services', 'Service')
    for service in Service.objects.all():
        changed = []
        if not service.feature_items and service.features:
            service.feature_items = [
                {'icon': icon.strip(), 'title': _text(title), 'text': _text(text)}
                for icon, title, text in FEATURE_RE.findall(service.features)
            ]
            changed.append('feature_items')
        if not service.benefit_items and service.benefits:
            service.benefit_items = [
                {'title': _text(title).rstrip(':').strip(), 'text': _text(text)}
                for title, text in BENEFIT_RE.findall(service.benefits)
            ]
            changed.append('benefit_items')
        if not service.process_items and service.process:
            service.process_items = [
                {'title': _text(title), 'text': _text(text)}
                for title, text in PROCESS_RE.findall(service.process)
            ]
            changed.append('process_items')
        if not service.faq_items and service.faq:
            try:
                data = json.loads(service.faq)
                service.faq_items = [
                    {'question': str(f.get('question', '')).strip(), 'answer': str(f.get('answer', '')).strip()}
                    for f in data if isinstance(f, dict) and f.get('question')
                ]
                changed.append('faq_items')
            except (ValueError, TypeError):
                pass
        if changed:
            service.save(update_fields=changed)


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_structured_sections'),
    ]

    operations = [
        migrations.RunPython(convert, migrations.RunPython.noop),
    ]
