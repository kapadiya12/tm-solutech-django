"""Gemini call with a backup model. Plain HTTPS via requests (no SDK)."""
import logging

import requests

log = logging.getLogger(__name__)
URL = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'


class AIError(Exception):
    pass


def generate(cfg, system, history):
    """history: [{'role': 'user'|'model', 'text': str}] ending with the visitor's message. Returns (text, model)."""
    contents = [{'role': h['role'], 'parts': [{'text': h['text']}]} for h in history]
    body = {
        'systemInstruction': {'parts': [{'text': system}]},
        'contents': contents,
        'generationConfig': {'temperature': float(cfg.temperature), 'maxOutputTokens': 900},
        'safetySettings': [{'category': c, 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'} for c in (
            'HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH', 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT')],
    }
    last_error = None
    for model in dict.fromkeys([cfg.model, cfg.backup_model]):   # unique, in order
        try:
            r = requests.post(URL.format(model=model), json=body, headers={'x-goog-api-key': cfg.key}, timeout=40)
        except requests.RequestException as e:
            last_error = e
            continue
        if r.status_code in (429, 500, 502, 503, 504):
            last_error = f'{model}: HTTP {r.status_code}'
            continue
        if not r.ok:
            log.warning('Gemini error %s: %s', r.status_code, r.text[:300])
            raise AIError(f'HTTP {r.status_code}')
        data = r.json()
        try:
            text = ''.join(p.get('text', '') for p in data['candidates'][0]['content']['parts'])
        except (KeyError, IndexError):
            text = ''
        if text.strip():
            return text, model
        last_error = f'{model}: empty reply'
    log.warning('Gemini unavailable: %s', last_error)
    raise AIError(str(last_error))
