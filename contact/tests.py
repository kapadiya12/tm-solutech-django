import time

from django.core import mail, signing
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import TOKEN_SALT
from .models import ContactInquiry


def aged_token(seconds=10):
    return signing.dumps(int(time.time()) - seconds, salt=TOKEN_SALT)


VALID = {
    'topic': 'New project',
    'name': 'Priya Shah',
    'company': 'Acme Industries',
    'email': '  Priya.Shah@Acme.COM ',
    'phone': '+91 98765 43210',
    'service': '',
    'message': 'We need help migrating our ERP servers to the cloud this quarter.',
    'consent': 'on',
    'website': '',
}


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', ADMIN_EMAIL='team@example.com')
class ContactFormTests(TestCase):
    url = reverse('contact:contact')

    def setUp(self):
        cache.clear()

    def post(self, ajax=False, **overrides):
        data = {**VALID, 'form_token': aged_token(), **overrides}
        headers = {'HTTP_X_REQUESTED_WITH': 'fetch'} if ajax else {}
        return self.client.post(self.url, data, **headers)

    # ---- happy path ----
    def test_valid_submission_saves_and_emails(self):
        res = self.post()
        self.assertRedirects(res, self.url)
        inquiry = ContactInquiry.objects.get()
        self.assertEqual(inquiry.email, 'priya.shah@acme.com')
        self.assertEqual(inquiry.subject, 'New project')
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ['team@example.com'])
        self.assertEqual(mail.outbox[1].to, ['priya.shah@acme.com'])
        self.assertIn('1–2 business days', mail.outbox[1].body)

    def test_ajax_success_returns_json_and_new_token(self):
        res = self.post(ajax=True)
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body['ok'])
        self.assertIn('form_token', body)

    def test_grouped_service_choice_accepted(self):
        self.post(service='Hardware Procurement')
        self.assertEqual(ContactInquiry.objects.get().service, 'Hardware Procurement')

    # ---- validation ----
    def assertFieldError(self, field, **overrides):
        res = self.post(ajax=True, **overrides)
        self.assertEqual(res.status_code, 400, res.content)
        self.assertIn(field, res.json()['errors'])
        self.assertFalse(ContactInquiry.objects.exists())

    def test_required_fields(self):
        for field in ('name', 'company', 'email', 'message'):
            with self.subTest(field=field):
                self.assertFieldError(field, **{field: ''})

    def test_name_rejects_digits_and_symbols(self):
        for bad in ('J', 'John123', 'Jo@hn', '<script>'):
            with self.subTest(bad=bad):
                self.assertFieldError('name', name=bad)

    def test_name_allows_real_names(self):
        for good in ("Anne-Marie O'Neil", 'Dr. R. K. Patel', 'Zoë Ångström'):
            with self.subTest(good=good):
                cache.clear()
                ContactInquiry.objects.all().delete()
                self.post(name=good)
                self.assertTrue(ContactInquiry.objects.exists(), good)

    def test_email_must_be_valid(self):
        self.assertFieldError('email', email='not-an-email')

    def test_phone_rules(self):
        for bad in ('12345', 'call me', '+91 98765 43210 99999 1'):
            with self.subTest(bad=bad):
                self.assertFieldError('phone', phone=bad)

    def test_message_length_and_links(self):
        self.assertFieldError('message', message='Too short')
        self.assertFieldError('message', message='x' * 2001)
        self.assertFieldError('message', message='see http://a.io http://b.io http://c.io http://d.io now please')

    def test_consent_required(self):
        data = {**VALID, 'form_token': aged_token()}
        data.pop('consent')
        res = self.client.post(self.url, data, HTTP_X_REQUESTED_WITH='fetch')
        self.assertEqual(res.status_code, 400)
        self.assertIn('consent', res.json()['errors'])

    def test_invalid_service_rejected(self):
        self.assertFieldError('service', service='Made Up Service')

    # ---- spam protection ----
    def test_honeypot_discards_silently(self):
        res = self.post(ajax=True, website='http://spam.example')
        self.assertTrue(res.json()['ok'])
        self.assertFalse(ContactInquiry.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_too_fast_submission_discarded(self):
        res = self.post(ajax=True, form_token=aged_token(0))
        self.assertTrue(res.json()['ok'])
        self.assertFalse(ContactInquiry.objects.exists())

    def test_forged_token_discarded(self):
        self.post(ajax=True, form_token='forged')
        self.assertFalse(ContactInquiry.objects.exists())

    def test_expired_form_asks_to_resubmit(self):
        res = self.post(ajax=True, form_token=aged_token(3 * 60 * 60))
        self.assertEqual(res.status_code, 400)
        self.assertIn('__all__', res.json()['errors'])

    def test_rate_limit(self):
        for _ in range(5):
            self.post(ajax=True)
        res = self.post(ajax=True)
        self.assertEqual(res.status_code, 429)
        self.assertEqual(ContactInquiry.objects.count(), 5)

    # ---- page ----
    def test_page_renders_with_token_and_prefill(self):
        res = self.client.get(self.url + '?service=Hardware+Procurement&topic=Support')
        self.assertContains(res, 'name="form_token"')
        self.assertContains(res, '<option value="Hardware Procurement" selected>')
        self.assertContains(res, '1–2 business days')
