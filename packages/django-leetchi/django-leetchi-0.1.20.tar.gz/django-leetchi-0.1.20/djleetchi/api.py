from django.utils.functional import memoize

from leetchi.api import LeetchiAPI

from . import settings


def _get_handler():
    return LeetchiAPI(settings.API_PARTNER_ID,
                      settings.API_PRIVATE_KEY,
                      settings.API_PRIVATE_KEY_PASSWORD,
                      sandbox=settings.API_USE_SANDBOX,
                      host=settings.API_HOST)


handler = memoize(_get_handler, {}, 0)()
