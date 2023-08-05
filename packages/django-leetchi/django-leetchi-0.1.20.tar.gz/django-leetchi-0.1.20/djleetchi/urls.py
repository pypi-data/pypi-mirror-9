from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

from . import views

urlpatterns = patterns(
    '',
    url(r'^wallet/detail/(?P<wallet_id>\d+)/$',
        staff_member_required(views.WalletDetailView.as_view()),
        name='leetchi_wallet_detail'),

    url(r'^contribution/detail/(?P<contribution_id>\d+)/$',
        staff_member_required(views.ContributionDetailView.as_view()),
        name='leetchi_contribution_detail'),

    url(r'^user/detail/(?P<user_id>\d+)/$',
        staff_member_required(views.UserDetailView.as_view()),
        name='leetchi_user_detail'),

    url(r'^refund/detail/(?P<refund_id>\d+)/$',
        staff_member_required(views.RefundDetailView.as_view()),
        name='leetchi_refund_detail'),

    url(r'^transfer/detail/(?P<transfer_id>\d+)/$',
        staff_member_required(views.TransferDetailView.as_view()),
        name='leetchi_transfer_detail'),

    url(r'^transferrefund/detail/(?P<transferrefund_id>\d+)/$',
        staff_member_required(views.TransferRefundDetailView.as_view()),
        name='leetchi_transferrefund_detail'),

    url(r'^withdrawal/detail/(?P<withdrawal_id>\d+)/$',
        staff_member_required(views.WithdrawalDetailView.as_view()),
        name='leetchi_withdrawal_detail'),
)
