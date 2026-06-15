from django.urls import path
from . import views
from transactions import views as transaction_views
from accounts import views as account_views

urlpatterns = [

    path(
        'deposit/',
        views.deposit_view,
        name='deposit'
    ),

    path(
        'buy/',
        views.buy_view,
        name='buy'
    ),

    path(
        'internal-transfer/',
        views.internal_transfer_view,
        name='internal_transfer'
    ),

    path(
        'internal-confirm/',
        views.internal_confirm_view,
        name='internal_confirm'
    ),

    path(
        'history/',
        views.history_view,
        name='history'
    ),

    path(
        'external-wallet/',
        views.external_wallet_view,
        name='external_wallet'
    ),

    path(
        'external-confirm/',
        views.external_confirm_view,
        name='external_confirm'
    ),

    path(
        'sell/',
        views.sell_view,
        name='sell'
    ),

    path(
        'edit-transaction/<int:pk>/',
        account_views.edit_transaction_view,
        name='edit_transaction'
    ),

    path(
        'cancel-test/<int:pk>/',
        views.cancel_transaction_view,
        name='cancel_transaction'
    ),
]