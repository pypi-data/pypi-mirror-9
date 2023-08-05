import sys
import time

from datetime import datetime, timedelta

from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--gap',
                    action='store',
                    type='int',
                    dest='gap',
                    default=30,
                    help='Gap bettween two sync'),
        make_option('--range',
                    action='store',
                    type='int',
                    dest='range',
                    default=1000,
                    help='Range between each querysets'),
        make_option('--limit',
                    action='store',
                    type='int',
                    dest='limit',
                    default=None,
                    help='Limit wallets to sync'),
        make_option('--sleep',
                    action='store',
                    type='float',
                    dest='sleep',
                    default=None,
                    help='Sleep between each sync'),
    )

    can_import_settings = True

    def handle(self, *args, **options):
        from leetchi.exceptions import APIError, DecodeError

        from djleetchi.models import Wallet

        qs = Wallet.objects.filter(models.Q(last_synced__lte=datetime.now() - timedelta(minutes=options.get('gap'))) |
                                   models.Q(last_synced__isnull=True)).extra({'has_last_synced': 'CASE WHEN last_synced IS NULL THEN 0 ELSE 1 END'}).order_by('has_last_synced', 'last_synced', 'id')

        limit = options.get('limit') or qs.count()
        sleep = options.get('sleep')

        for offset in range(0, limit, options.get('range')):

            wallets = qs[offset:offset + options.get('range')]

            for wallet in wallets:
                try:
                    last_synced = wallet.last_synced

                    wallet.sync_amount()

                    print u'Sync wallet for user %s (last synced at %s)' % (wallet.user, last_synced)

                    if sleep:
                        time.sleep(sleep)

                except (APIError, DecodeError), e:
                    sys.stdout.write(e)
