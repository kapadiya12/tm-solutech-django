"""Email validation: format, provider rules (Gmail), typo suggestions,
disposable-domain blocking and a DNS check that the domain receives mail."""
import re

from django.core.cache import cache

FORMAT_RE = re.compile(
    r'^(?!.*\.\.)[a-z0-9._%+\-]+@[a-z0-9](?:[a-z0-9\-]*[a-z0-9])?'
    r'(?:\.[a-z0-9](?:[a-z0-9\-]*[a-z0-9])?)*\.[a-z]{2,24}$'
)
GMAIL_LOCAL_RE = re.compile(r'^[a-z0-9](?:[a-z0-9.]*[a-z0-9])?$')

PROVIDERS = [
    'gmail.com', 'yahoo.com', 'yahoo.co.in', 'yahoo.in', 'outlook.com', 'hotmail.com', 'live.com',
    'icloud.com', 'me.com', 'rediffmail.com', 'protonmail.com', 'proton.me', 'zoho.com', 'zohomail.in',
    'aol.com', 'msn.com', 'gmx.com', 'yandex.com', 'mail.com',
    'googlemail.com', 'hotmail.co.in', 'outlook.in', 'ymail.com', 'rocketmail.com', 'live.in', 'mac.com', 'pm.me',
]
TYPO_STRICT = {'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'rediffmail.com', 'icloud.com'}
# Common top-level-domain typos -> the intended ending
TLD_FIXES = {'con': 'com', 'cmo': 'com', 'ocm': 'com', 'comm': 'com', 'coom': 'com', 'cm': 'com', 'vom': 'com', 'xom': 'com',
             'om': 'com', 'nett': 'net', 'ne': 'net', 'nte': 'net', 'ogr': 'org', 'orgg': 'org', 'inn': 'in', 'co.inn': 'co.in'}
# Provider username rules: (pattern for the part before the +, min, max, message)
PROVIDER_RULES = {
    ('yahoo.com', 'yahoo.co.in', 'yahoo.in', 'ymail.com', 'rocketmail.com'): (
        re.compile(r'^[a-z][a-z0-9._]*[a-z0-9]$'), 4, 32,
        'Yahoo usernames start with a letter and use letters, numbers, dots or underscores (4 to 32 characters).'),
    ('outlook.com', 'hotmail.com', 'live.com', 'msn.com', 'outlook.in', 'hotmail.co.in'): (
        re.compile(r'^[a-z0-9][a-z0-9._\-]*$'), 1, 64,
        'Outlook and Hotmail addresses start with a letter or number and use letters, numbers, dots, hyphens or underscores.'),
    ('icloud.com', 'me.com', 'mac.com'): (
        re.compile(r'^[a-z][a-z0-9._]*[a-z0-9]$'), 3, 20,
        'iCloud usernames start with a letter and are 3 to 20 characters.'),
    ('rediffmail.com',): (
        re.compile(r'^[a-z][a-z0-9._]*$'), 4, 30,
        'Rediffmail usernames start with a letter and are 4 to 30 characters.'),
    ('protonmail.com', 'proton.me', 'pm.me'): (
        re.compile(r'^[a-z0-9][a-z0-9._\-]*[a-z0-9]$'), 3, 40,
        'Proton usernames are 3 to 40 letters, numbers, dots, hyphens or underscores.'),
}
DISPOSABLE = {
    'mailinator.com', 'yopmail.com', 'guerrillamail.com', 'guerrillamail.info', 'sharklasers.com',
    '10minutemail.com', 'tempmail.com', 'temp-mail.org', 'throwawaymail.com', 'trashmail.com',
    'getnada.com', 'dispostable.com', 'maildrop.cc', 'fakeinbox.com', 'mintemail.com',
    'mailnesia.com', 'tempail.com', 'emailondeck.com', 'mohmal.com', 'moakt.com',
    'temp-mail.io', 'tempmailo.com', 'tmpmail.org', 'tmpmail.net', 'burnermail.io', 'spamgourmet.com',
    'mailcatch.com', 'mytemp.email', 'tempinbox.com', 'discard.email', 'emailfake.com', 'fakemail.net',
    'guerrillamailblock.com', 'grr.la', 'pokemail.net', 'spam4.me', 'mailpoof.com', 'inboxkitten.com',
    'harakirimail.com', 'mailsac.com', 'tempr.email', 'byom.de', 'cock.li', 'dropmail.me', '1secmail.com',
    '1secmail.org', '1secmail.net', 'linshiyouxiang.net', 'mail.tm', 'getairmail.com', 'anonaddy.me',
    'trashmail.de', 'wegwerfmail.de', 'spambox.us', 'mailforspam.com', 'yopmail.fr', 'yopmail.net',
}
EXTRACT_RE = re.compile(r'<\s*([^<>\s]+@[^<>\s]+)\s*>')


def normalise_email(raw):
    """Tidy what people paste: 'Name <a@b.com>', 'mailto:a@b.com', trailing dots, full-width @, stray quotes."""
    v = (raw or '').strip()
    m = EXTRACT_RE.search(v)
    if m:
        v = m.group(1)
    v = v.replace('\uff20', '@').replace('\u200b', '').strip().strip('"\'<>,;').strip()
    if v.lower().startswith('mailto:'):
        v = v[7:]
    v = v.split('?')[0].rstrip('.').lower()
    return v


def _lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def suggest_domain(domain):
    """Closest well-known provider for a likely typo, or None."""
    domain = (domain or '').lower().strip('.')
    if not domain or domain in PROVIDERS:
        return None
    name = domain.split('.')[0]
    best, best_score = None, 99
    for p in PROVIDERS:
        pname = p.split('.')[0]
        if len(pname) < 4 or abs(len(pname) - len(name)) > 2:
            continue   # short names like me.com would match far too much
        score = min(_lev(domain, p), _lev(name, pname) + (0 if '.' in domain else 1))
        if score < best_score:
            best, best_score = p, score
    limit = 1 if len(name) <= 3 else 2
    if best and best_score <= limit + (1 if '.' not in domain else 0):
        return best
    return None


def domain_accepts_mail(domain):
    """True / False when DNS gives a definite answer; None if it can't be checked (never block on that)."""
    key = 'email-domain:' + domain
    cached = cache.get(key)
    if cached is not None:
        return cached
    try:
        import dns.exception
        import dns.resolver
    except ImportError:
        return None
    result = None
    try:
        dns.resolver.resolve(domain, 'MX', lifetime=3)
        result = True
    except dns.resolver.NXDOMAIN:
        result = False
    except dns.resolver.NoAnswer:
        try:  # no MX: mail can still go to the A record
            dns.resolver.resolve(domain, 'A', lifetime=3)
            result = True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            result = False
        except dns.exception.DNSException:
            result = None
    except dns.exception.DNSException:
        result = None
    if result is not None:
        cache.set(key, result, 24 * 60 * 60)
    return result


def check_email(email, check_dns=True):
    """Return (error_message or None, suggested_email or None)."""
    email = normalise_email(email)
    if not email:
        return 'Please enter your work email.', None
    if ' ' in email:
        return 'Email addresses cannot contain spaces.', None
    if email.count('@') != 1:
        return 'An email address needs exactly one @, like name@company.com.', None
    local, domain = email.split('@')
    if not local:
        return 'Add your name before the @.', None
    if not domain:
        return 'Add the domain after the @, like gmail.com.', None
    if local.startswith('.') or local.endswith('.'):
        return 'The part before the @ cannot start or end with a dot.', None
    if '..' in email:
        return 'An email address cannot contain two dots in a row.', None
    if any(c in local for c in '()[]\\,;:<>"'):
        return 'The part before the @ contains characters that are not allowed.', None
    suggestion = suggest_domain(domain)
    fix = f'{local}@{suggestion}' if suggestion else None
    if '.' not in domain:
        return 'The domain is incomplete. Did you forget ".com"?', fix
    # Typos in the ending: company.con -> company.com
    for bad, good in sorted(TLD_FIXES.items(), key=lambda x: -len(x[0])):
        if domain.endswith('.' + bad) and domain.rsplit('.', bad.count('.') + 1)[0]:
            fixed_domain = domain[: -len(bad)] + good
            return f'Check the ending of your email: did you mean @{fixed_domain}?', f'{local}@{suggest_domain(fixed_domain) or fixed_domain}'
    labels = domain.split('.')
    if any(not l or len(l) > 63 or l.startswith('-') or l.endswith('-') for l in labels):
        return 'The domain part of your email is not valid.', fix
    if labels[-1].isdigit():
        return 'That looks like an IP address. Please use an email domain, like company.com.', None
    if len(email) > 254 or len(local) > 64 or not FORMAT_RE.match(email):
        return 'Please enter a valid email address, like name@company.com.', fix
    if domain in ('gmail.com', 'googlemail.com'):
        bare = local.split('+')[0]
        if not GMAIL_LOCAL_RE.match(bare):
            return 'Gmail addresses use only letters, numbers and dots.', None
        if not 6 <= len(bare.replace('.', '')) <= 30:
            return 'Gmail usernames are 6 to 30 characters long.', None
    for domains, (pattern, lo, hi, message) in PROVIDER_RULES.items():
        if domain in domains:
            bare = local.split('+')[0]
            if not (pattern.match(bare) and lo <= len(bare) <= hi):
                return message, None
            break
    if domain in DISPOSABLE or any(domain.endswith('.' + d) for d in DISPOSABLE):
        return 'Please use your work or personal email, not a temporary one.', None
    if suggestion in TYPO_STRICT and domain not in PROVIDERS:
        return f'Check the spelling of your email: did you mean @{suggestion}?', fix
    if fix and check_dns:
        # A typo of a big provider (e.g. gmal.com): suggest, and reject if it can't receive mail
        if domain_accepts_mail(domain) is False:
            return f'"{domain}" does not receive email. Did you mean {suggestion}?', fix
    elif check_dns and domain_accepts_mail(domain) is False:
        return f'"{domain}" does not receive email. Please check the spelling.', None
    return None, fix
