from django.db import models
from django.contrib.contenttypes.models import ContentType

from .models import TransferRefund, Transfer, Contribution, Refund
from .helpers import queryset_to_dict


def transfer_refund(instance, user):
    contenttype = ContentType.objects.get_for_model(instance)

    transfers = Transfer.objects.filter(object_id=instance.pk, content_type=contenttype)

    transfer_refund_list = []

    if len(transfers):
        for transfer in transfers:
            transfer_refund = TransferRefund()
            transfer_refund.content_object = instance
            transfer_refund.transfer = transfer
            transfer_refund.user = user
            transfer_refund.save(sync=True)

            transfer_refund_list.append(transfer_refund)

        return transfer_refund_list

    return False


def refund(instance, user):
    contenttype = ContentType.objects.get_for_model(instance)

    contributions = Contribution.objects.filter(object_id=instance.pk,
                                                content_type=contenttype,
                                                is_success=True,
                                                is_completed=True)

    contribution_ids = [contribution.pk for contribution in contributions]

    qs = (Refund.objects.filter(contribution__in=contribution_ids)
          .filter(models.Q(is_success=True, is_completed=True) | models.Q(is_success=False, is_completed=False)))

    refunds = queryset_to_dict(qs, key='contribution_id', singular=False)

    refund_list = []

    if len(contributions):
        for contribution in contributions:
            if not contribution.pk in refunds:
                refund = Refund()
                refund.content_object = instance
                refund.contribution = contribution
                refund.user = user
                refund.save(sync=True)

                refund_list.append(transfer_refund)

        return refund_list

    return False
