import logging
import os

from django.apps import AppConfig
from django.core.signals import request_started

logger = logging.getLogger(__name__)


def _reset_admin_from_env(sender, **kwargs):
    """One-time admin access recovery for hosts without a shell.

    Set ADMIN_RESET_PASSWORD (and optionally ADMIN_RESET_USERNAME, default "admin")
    in the host's environment variables. On the first request after start-up the
    account is created or its password set, then this hook disconnects itself.
    Remove the variable once you have logged in and changed the password.
    The password is never stored in the codebase.
    """
    request_started.disconnect(_reset_admin_from_env, dispatch_uid='admin-env-reset')
    password = os.environ.get('ADMIN_RESET_PASSWORD', '')
    if not password:
        return
    username = os.environ.get('ADMIN_RESET_USERNAME', 'admin').strip() or 'admin'
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(username=username).first() or User(username=username, email='admin@tmsolutech.com')
        changed = not user.pk or not user.check_password(password) or not (user.is_active and user.is_staff and user.is_superuser)
        if changed:
            user.set_password(password)
            user.is_active = user.is_staff = user.is_superuser = True
            user.save()
            logger.warning('Admin access restored for "%s" from ADMIN_RESET_PASSWORD. Remove the variable now.', username)
    except Exception:
        logger.exception('Admin reset from environment failed')


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        if os.environ.get('ADMIN_RESET_PASSWORD'):
            request_started.connect(_reset_admin_from_env, dispatch_uid='admin-env-reset')
