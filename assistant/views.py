import json
import re

from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .ai import AIError, generate
from .knowledge import build_system, split_suggestions
from .models import AssistantSettings, Conversation

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _daily_key():
    return 'assistant:daily:' + timezone.localdate().isoformat()


def _save_lead(convo, lead):
    from contact.models import ContactInquiry
    email = lead.get('email', '').strip()
    phone = lead.get('phone', '').strip()
    if convo.lead_id or not lead.get('name') or not (EMAIL_RE.match(email) or len(re.sub(r'\D', '', phone)) >= 8):
        return None
    turns = '\n'.join(f'{"Visitor" if t["role"] == "user" else "Assistant"}: {t["text"]}' for t in convo.transcript[-12:])
    inquiry = ContactInquiry.objects.create(
        name=lead['name'][:200], email=email if EMAIL_RE.match(email) else '', phone=phone[:20],
        company=lead.get('company', '')[:200], subject='Enquiry via AI assistant',
        service=lead.get('need', '')[:200],
        message=(lead.get('need') or 'Enquiry from the website chat.') + '\n\n--- Chat ---\n' + turns,
    )
    convo.lead = inquiry
    return inquiry


@require_POST
def chat(request):
    cfg = AssistantSettings.get()
    try:
        data = json.loads(request.body or '{}')
    except ValueError:
        return JsonResponse({'error': 'bad request'}, status=400)
    message = ' '.join(str(data.get('message', '')).split())[:1200]
    if not message:
        return JsonResponse({'error': 'empty'}, status=400)
    if not cfg.enabled or not cfg.ready:
        return JsonResponse({'reply': cfg.busy_message, 'suggestions': []})

    convo = None
    if data.get('token'):
        convo = Conversation.objects.filter(token=data['token']).first()
    if convo is None:
        convo = Conversation(page=str(data.get('page', ''))[:300], title=message[:120])

    if convo.visitor_messages >= cfg.max_messages or (cache.get(_daily_key()) or 0) >= cfg.daily_limit:
        return JsonResponse({'reply': cfg.limit_message, 'suggestions': [], 'token': str(convo.token), 'limited': True})

    history = convo.transcript[-(cfg.history_turns * 2):] + [{'role': 'user', 'text': message}]
    try:
        raw, model = generate(cfg, build_system(cfg), history)
    except AIError:
        return JsonResponse({'reply': cfg.busy_message, 'suggestions': [], 'token': str(convo.token) if convo.pk else ''})

    reply, suggestions, lead = split_suggestions(raw)
    convo.transcript = convo.transcript + [{'role': 'user', 'text': message}, {'role': 'model', 'text': reply}]
    convo.visitor_messages += 1
    convo.model = model
    convo.is_read = False
    lead_saved = bool(lead and cfg.collect_leads and _save_lead(convo, lead))
    convo.save()
    try:
        cache.incr(_daily_key())
    except ValueError:
        cache.set(_daily_key(), 1, 60 * 60 * 26)
    return JsonResponse({'reply': reply, 'suggestions': suggestions if cfg.show_suggestions else [],
                         'token': str(convo.token), 'lead': lead_saved})
