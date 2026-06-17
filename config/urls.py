from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('accounts.urls')),

    path('', include('transactions.urls')),

    path(
        'admin-dashboard/',
        core_views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'update-deposit-status/',
        core_views.update_deposit_status,
    ),

    path(
        'update-buy-status/',
        core_views.update_buy_status,
    ),

    path(
        'update-withdrawal-status/',
        core_views.update_withdrawal_status,
    ),

    path(
        'update-sell-status/',
        core_views.update_sell_status,
    ),

    path(
        'edit-transaction/<int:id>/',
        account_views.edit_transaction_view,
        name='edit_transaction'
    ),

]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

from django.views.generic import TemplateView

urlpatterns += [

]