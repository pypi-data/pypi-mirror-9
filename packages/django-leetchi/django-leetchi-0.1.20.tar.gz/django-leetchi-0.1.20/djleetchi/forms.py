import logging

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from leetchi.exceptions import APIError, DecodeError

from .models import Contribution, Transfer, Beneficiary, Withdrawal, get_pending_amount
from .helpers import get_payer

from django_iban.forms import IBANFormField, SWIFTBICFormField

logger = logging.getLogger('django.leetchi')


class WithdrawalForm(forms.ModelForm):
    bank_account_owner_name = forms.CharField(label=_(u'Name of the bank account owner'),
                                              required=True)
    bank_account_owner_address = forms.CharField(label=_(u'Address of the bank account owner'),
                                                 required=True)
    bank_account_iban = IBANFormField(label=_(u'IBAN of the bank account owner'),
                                      required=True,
                                      help_text=_(u'Without spaces'))
    bank_account_bic = SWIFTBICFormField(label=_(u'BIC of the bank account owner'),
                                         required=True,
                                         help_text=_(u'Without spaces'))

    class Meta:
        model = Withdrawal
        fields = ('amount', 'client_fee_amount', )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.wallet = kwargs.pop('wallet', None)
        self.content_object = kwargs.pop('content_object', None)
        self.sync = kwargs.pop('sync', True)

        super(WithdrawalForm, self).__init__(*args, **kwargs)

        self.fields['amount'] = forms.DecimalField(label=_('Amount'), help_text=_('Value in decimal, e.g. 20.50'))

    def is_personal_amount_enough(self, amount):
        payer = get_payer(self.user)

        personal_amount = payer.personal_wallet_amount_converted

        return personal_amount >= float(amount)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if self.content_object or not self.user:
            return amount

        payer = get_payer(self.user)

        amount_converted = payer.personal_wallet_amount_converted

        if not self.is_personal_amount_enough(amount):
            error_message = _('Your personal amount %(personal_amount)s is '
                              'not enough to make this withdrawal %(amount)s')

            raise forms.ValidationError(error_message % {
                'personal_amount': amount_converted,
                'amount': amount
            })

        withdrawal_amount = get_pending_amount(self.user) / 100

        if withdrawal_amount:
            if not self.is_personal_amount_enough(amount + withdrawal_amount):
                error_message = _('You can\'t make a withdrawal of %(amount)s, you already have '
                                  '%(withdrawal_amount)s of pending withdrawals and your personal amount is only %(personal_amount)s')

                raise forms.ValidationError(error_message % {
                    'personal_amount': amount_converted,
                    'amount': amount,
                    'withdrawal_amount': withdrawal_amount
                })

        return amount

    def save(self):
        try:
            beneficiary = Beneficiary(user=self.user)

            for k, v in self.cleaned_data.items():
                setattr(beneficiary, k, v)

            beneficiary.save(sync=True)

            self.instance.beneficiary = beneficiary

            if self.wallet:
                self.instance.wallet = self.wallet

            self.instance.user = self.user
            self.instance.amount = self.cleaned_data['amount'] * 100
            self.instance.content_object = self.content_object or self.user
            self.instance.save(sync=self.sync)
        except (APIError, DecodeError), e:
            logger.error(e)

            self.instance.error = e
        else:
            self.instance.error = None

        return self.instance


class ContributionForm(forms.Form):
    amount = forms.DecimalField(label=_("Amount"), widget=forms.TextInput,
                                help_text=_('Value in decimal, e.g. 20.50'))

    def save(self, request, user, return_url, template_url=None):
        try:
            current_site = Site.objects.get_current()

            protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")

            absolute_url = request.META.get('HTTP_HOST', current_site.domain)

            return_url = u"%s://%s%s" % (
                protocol,
                unicode(absolute_url),
                return_url
            )

            amount = int(float(self.cleaned_data.get('amount')) * 100)

            contribution = Contribution()
            contribution.content_object = user
            contribution.user = request.user
            contribution.wallet_id = 0
            contribution.amount = amount
            contribution.return_url = return_url
            contribution.target = user

            template_url = u"https://%s%s" % (
                unicode(absolute_url),
                template_url
            )

            contribution.template_url = template_url

            contribution.save(sync=True)
        except (APIError, DecodeError), e:
            logger.error(e)
            return False
        else:
            return contribution


class TransferForm(forms.Form):
    amount = forms.CharField(label=_("Amount"), widget=forms.TextInput,
                             help_text=_('Value in decimal, e.g. 20.50'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(TransferForm, self).__init__(*args, **kwargs)

    def clean_amount(self):

        payer = get_payer(self.user)

        amount = self.cleaned_data.get('amount')

        if not self.is_personal_amount_enough(amount):
            error_message = _('Your personal amount %(personal_amount)s is \
                              not enough to make this transfer %(amount)s')

            amount_converted = payer.personal_wallet_amount_converted

            raise forms.ValidationError(error_message % {
                'personal_amount': amount_converted,
                'amount': amount
            })

        return amount

    def is_personal_amount_enough(self, amount):
        payer = get_payer(self.user)

        personal_amount = payer.personal_wallet_amount_converted

        return personal_amount >= float(amount)

    def save(self, payer_user, beneficiary_user):
        try:
            transfer = Transfer()
            transfer.content_object = beneficiary_user
            transfer.user = payer_user
            transfer.payer = payer_user
            transfer.amount = int(float(self.cleaned_data.get('amount')) * 100)
            transfer.beneficiary = beneficiary_user
            transfer.beneficiary_wallet_id = 0
            transfer.save()
        except (APIError, DecodeError), e:
            logger.error(e)
            return False
        else:
            return transfer
