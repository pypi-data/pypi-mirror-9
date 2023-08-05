from optparse import make_option

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--limit',
                    action='store',
                    type='int',
                    dest='limit',
                    default=100,
                    help='Limit resources to sync'),
        make_option('--name',
                    action='store',
                    type='string',
                    dest='name',
                    default=None,
                    help='Name of resource you want to sync'),
    )

    can_import_settings = True

    @property
    def resources(self):
        from djleetchi.models import Contribution, Withdrawal, Refund

        return {
            'refund': Refund,
            'withdrawal': Withdrawal,
            'contribution': Contribution
        }

    def handle(self, *args, **options):
        from djleetchi.tasks import sync_status

        from celery import group

        resources = self.resources

        name = options.get('name', None)

        if name and name not in resources:
            raise CommandError('Resource name %s does not exist or not available to sync' % name)

        limit = options.get('limit')

        for resource_name, klass in resources.iteritems():
            if name and resource_name != name:
                continue

            params = {
                'is_completed': False,
                '%s__isnull' % klass.Api.resource_field: False
            }

            resource_ids = klass.objects.filter(**params).values_list('id', flat=True).order_by('-id')[:limit]

            tasks = [sync_status.subtask(args=(klass, resource_id, )) for resource_id in resource_ids]

            job = group(tasks)

            job.apply_async()

            print 'Syncing %s %s' % (limit, resource_name)
