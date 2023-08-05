from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .permission import FeinCMSPermissionMiddleware, LoginPermissionMiddlewareMixin


def check_feincms_page():
    """
    Check that FeinCMSLoginRequiredMiddleware isn't being used without its dependency.

    FeinCMSLoginRequiredMiddleware needs feincms.context_processors.add_page_if_missing.
    """
    processors = settings.TEMPLATE_CONTEXT_PROCESSORS

    if 'feincms.context_processors.add_page_if_missing' in processors:
        return

    error_message = ' '.join((
        "TEMPLATE_CONTEXT_PROCESSORS does not contain add_page_if_missing.",
        "FeinCMSLoginRequiredMiddleware requires the FeinCMS page middleware",
        "to be installed. Ensure your TEMPLATE_CONTEXT_PROCESSORS setting",
        "includes 'feincms.context_processors.add_page_if_missing'.",
    ))
    raise ImproperlyConfigured(error_message)


class FeinCMSLoginRequiredMiddleware(
    LoginPermissionMiddlewareMixin,
    FeinCMSPermissionMiddleware
):
    """
    Middleware that requires a user to be authenticated to view any page with an
    access_state of STATE_AUTH_ONLY.

    Requires authentication middleware, template context processors, and FeinCMS's
    add_page_if_missing middleware to be loaded. You'll get an error if they aren't.
    """
    def __init__(self, check=True):
        if check:
            check_feincms_page()
