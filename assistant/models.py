import os
import uuid

from django.db import models

MODEL_CHOICES = [
    ('gemini-3.5-flash-lite', 'Gemini 3.5 Flash-Lite (fastest, recommended)'),
    ('gemini-3.5-flash', 'Gemini 3.5 Flash (smarter)'),
    ('gemini-3.8-flash', 'Gemini 3.8 Flash (newest)'),
    ('gemini-2.5-flash', 'Gemini 2.5 Flash (stable)'),
]


class AssistantSettings(models.Model):
    """The website AI assistant ("Tima"), edited in Admin → AI Assistant."""
    enabled = models.BooleanField('Show the assistant on the website', default=True)
    name = models.CharField('Assistant name', max_length=30, default='Tima')
    tagline = models.CharField('Line under the name', max_length=60, default='TM Solutech AI · replies in seconds')
    launcher_label = models.CharField('Button text', max_length=30, default='Ask Tima')
    greeting = models.TextField('First message', max_length=500, default=(
        "Hi, I'm Tima, TM Solutech's AI guide. I can help you find the right IT solution: cloud, cybersecurity, "
        "networks, AI or hardware. What are you working on?"))
    quick_replies = models.TextField('Suggested questions', blank=True, help_text='One per line, shown as buttons at the start.', default=(
        'What services do you offer?\nHelp me with SEBI CSCRF compliance\nDo you provide 24/7 support?\nI want to move to the cloud'))
    personality = models.TextField('Personality & tone', blank=True, default=(
        'Warm, confident and precise, like a senior IT consultant who explains things simply. '
        'Short paragraphs, no jargon unless the visitor uses it.'))
    extra_knowledge = models.TextField('Extra things the assistant should know', blank=True, help_text=(
        'Facts, policies or details to use. Everything on the website (services, FAQs, industries, team…) is learned automatically.'))
    collect_leads = models.BooleanField('Collect leads (save enquiries from chats)', default=True)
    show_suggestions = models.BooleanField('Suggest follow-up questions after each answer', default=True)
    show_on_phones = models.BooleanField('Show on phones', default=True)
    position = models.CharField('Where Tima sits', max_length=5, choices=[('left', 'Bottom left'), ('right', 'Bottom right')], default='left')
    show_nudge = models.BooleanField('Show a pop-up message on the first visit', default=True)
    nudge_text = models.TextField('Pop-up messages', blank=True, default=(
        'Need help choosing the right IT solution? Ask me 👋\n'
        'Looking at {page}? I can explain it in 30 seconds.\n'
        'Planning a cloud move or security upgrade? Let\'s talk.'),
        help_text='One per line. A random one is shown; {page} is replaced with the page the visitor is on.')
    page_suggestions = models.BooleanField('Suggest questions about the page the visitor is on', default=True)
    nudge_delay = models.PositiveSmallIntegerField('Pop-up after (seconds)', default=8)
    placeholder = models.CharField('Message box placeholder', max_length=60, default='Ask about services, support, pricing…')
    footer_note = models.CharField('Small note under the message box', max_length=80, blank=True, default='AI answers can make mistakes. Verify important details with our team.')
    # AI
    gemini_key = models.CharField('Gemini API key', max_length=200, blank=True,
                                  help_text='Leave empty to use the GEMINI_API_KEY server setting (recommended).')
    model = models.CharField('AI model', max_length=60, choices=MODEL_CHOICES, default='gemini-3.5-flash-lite')
    backup_model = models.CharField('Backup model (used when the main one is busy)', max_length=60, choices=MODEL_CHOICES, default='gemini-3.5-flash')
    temperature = models.DecimalField('Creativity', max_digits=3, decimal_places=2, default=0.4,
                                      help_text='0 = most factual, 1 = most creative. 0.3–0.5 suits a business assistant.')
    history_turns = models.PositiveSmallIntegerField('Earlier messages the AI re-reads', default=10)
    max_messages = models.PositiveIntegerField('Messages per visitor conversation', default=30)
    daily_limit = models.PositiveIntegerField('Messages per day (whole site)', default=500, help_text='A safety cap on usage.')
    busy_message = models.CharField('When the AI is busy', max_length=200, default=(
        "I couldn't connect just now. Please try again in a moment, or call us on +91 79 4771 7070."))
    limit_message = models.CharField('After a limit is reached', max_length=200, default=(
        "We've covered a lot! For anything more, our team will be glad to help: call +91 79 4771 7070 or use the contact form."))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = verbose_name_plural = 'AI assistant settings'

    def __str__(self):
        return 'AI assistant'

    @classmethod
    def get(cls):
        return cls.objects.first() or cls.objects.create()

    @property
    def key(self):
        return (self.gemini_key or os.getenv('GEMINI_API_KEY', '')).strip()

    @property
    def ready(self):
        return bool(self.key)

    @property
    def quick_reply_list(self):
        return [q.strip() for q in (self.quick_replies or '').splitlines() if q.strip()][:6]


class TrainedAnswer(models.Model):
    """An exact answer the team taught the assistant. Used before anything else."""
    question = models.CharField('When visitors ask', max_length=300)
    answer = models.TextField('The assistant answers')
    is_active = models.BooleanField('Use this answer', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.question


class Conversation(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    page = models.CharField('Started on', max_length=300, blank=True)
    title = models.CharField(max_length=200, blank=True)
    transcript = models.JSONField(default=list, blank=True, help_text='[{"role": "user"|"model", "text": "..."}]')
    visitor_messages = models.PositiveIntegerField(default=0)
    model = models.CharField(max_length=60, blank=True)
    lead = models.ForeignKey('contact.ContactInquiry', null=True, blank=True, on_delete=models.SET_NULL, related_name='chats')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title or f'Chat {self.pk}'
