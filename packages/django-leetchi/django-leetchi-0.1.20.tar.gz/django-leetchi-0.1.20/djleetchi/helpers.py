import six

from collections import defaultdict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .util import load_class


def queryset_to_dict(qs, key='pk', singular=True):
    """
    Given a queryset will transform it into a dictionary based on ``key``.
    """
    if singular:
        result = {}
        for u in qs:
            result.setdefault(getattr(u, key), u)
    else:
        result = defaultdict(list)
        for u in qs:
            result[getattr(u, key)].append(u)
    return result


def _get_payer(user):
    from .models import Wallet

    return Wallet.objects.get_for_model(user).user


get_payer = getattr(settings, 'LEETCHI_PAYER_HELPER', _get_payer)

if not get_payer:
    raise ImproperlyConfigured('The required setting **LEETCHI_PAYER_HELPER** is missing.')
elif isinstance(get_payer, six.string_types):
    get_payer = load_class(get_payer)


def _get_wallet(resource):
    from .model import Wallet

    return Wallet.objects.get_for_model(resource).wallet


get_wallet = getattr(settings, 'LEETCHI_WALLET_HELPER', _get_wallet)

if not get_wallet:
    raise ImproperlyConfigured('The required setting **LEETCHI_WALLET_HELPER** is missing.')
elif isinstance(get_wallet, six.string_types):
    get_wallet = load_class(get_wallet)
