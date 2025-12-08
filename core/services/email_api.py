"""Email API helpers were removed as part of reverting the password-reset feature.

This module is intentionally left as a stub to avoid accidental usage.
If you need API-based sending in the future, re-add an implementation here.
"""

def send_email(*args, **kwargs):
    raise NotImplementedError("Email API helper was removed — use the project's SMTP configuration instead.")
