import re

from django import template
from django.contrib.contenttypes.models import ContentType

from djleetchi.models import (Contribution, Refund, Wallet,
                              Transfer, TransferRefund, Withdrawal)

register = template.Library()


class ResourcesNode(template.Node):
    def __init__(self, obj, var_name, klass):
        self.obj = template.Variable(obj)
        self.var_name = var_name
        self.klass = klass

    def render(self, context):
        try:
            obj = self.obj.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        results = self.klass.objects.filter(content_type=ContentType.objects.get_for_model(obj),
                                            object_id=obj.pk)

        if self.var_name:
            context[self.var_name] = results

        return ''


@register.tag
def get_resources_for(parser, token, klass):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)

    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    user, var_name = m.groups()

    return ResourcesNode(user, var_name, klass)


@register.tag
def get_contributions_for(parser, token):
    return get_resources_for(parser, token, Contribution)


@register.tag
def get_refunds_for(parser, token):
    return get_resources_for(parser, token, Refund)


@register.tag
def get_withdrawals_for(parser, token):
    return get_resources_for(parser, token, Withdrawal)


@register.tag
def get_transfers_for(parser, token):
    return get_resources_for(parser, token, Transfer)


@register.tag
def get_transferrefunds_for(parser, token):
    return get_resources_for(parser, token, TransferRefund)


@register.tag
def get_wallets_for(parser, token):
    return get_resources_for(parser, token, Wallet)
