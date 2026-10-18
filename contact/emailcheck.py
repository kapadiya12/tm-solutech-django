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
    'gmail.com', 'yahoo.com', 'yahoo.co.in', 'outlook.com', 'hotmail.com', 'live.com',
    'icloud.com', 'rediffmail.com', 'protonmail.com', 'zoho.com', 'aol.com', 'msn.com',
]
DISPOSABLE = {
    'mailinator.com', 'yopmail.com', 'guerrillamail.com', 'guerrillamail.info', 'sharklasers.com',
    '10minutemail.com', 'tempmail.com', 'temp-mail.org', 'throwawaymail.com', 'trashmail.com',
    'getnada.com', 'dispostable.com', 'maildrop.cc', 'fakeinbox.com', 'mintemail.com',
    'mailnesia.com', 'tempail.com', 'emailondeck.com', 'mohmal.com', 'moakt.com',
}


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
    email = (email or '').strip().lower()
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
    suggestion = suggest_domain(domain)
    fix = f'{local}@{suggestion}' if suggestion else None
    if '.' not in domain:
        return 'The domain is incomplete. Did you forget ".com"?', fix
    if len(email) > 254 or len(local) > 64 or not FORMAT_RE.match(email):
        return 'Please enter a valid email address, like name@company.com.', fix
    if domain in ('gmail.com', 'googlemail.com'):
        bare = local.split('+')[0]
        if not GMAIL_LOCAL_RE.match(bare):
            return 'Gmail addresses use only letters, numbers and dots.', None
        if not 6 <= len(bare.replace('.', '')) <= 30:
            return 'Gmail usernames are 6 to 30 characters long.', None
    if domain in DISPOSABLE:
        return 'Please use your work or personal email, not a temporary one.', None
    if fix and check_dns:
        # A typo of a big provider (e.g. gmal.com): suggest, and reject if it can't receive mail
        if domain_accepts_mail(domain) is False:
            return f'"{domain}" does not receive email. Did you mean {suggestion}?', fix
    elif check_dns and domain_accepts_mail(domain) is False:
        return f'"{domain}" does not receive email. Please check the spelling.', None
    return None, fix
