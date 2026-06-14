from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from accounts.models import WalletUser

from transactions.models import (
    Deposit,
    BuyOrder,
    Withdrawal,
    SellOrder
)

def admin_stats(request):

    total_users = WalletUser.objects.count()

    total_balance = WalletUser.objects.aggregate(
        Sum('balance')
    )['balance__sum'] or 0

    pending_deposits = Deposit.objects.filter(
        status='PENDING',
        created_at__lte=timezone.now() - timedelta(minutes=10)
    ).count()

    pending_buys = BuyOrder.objects.filter(
        status='PENDING',
        created_at__lte=timezone.now() - timedelta(minutes=10)
    ).count()

    pending_withdrawals = Withdrawal.objects.filter(
        status='PENDING',
        created_at__lte=timezone.now() - timedelta(minutes=10)
    ).count()

    pending_sells = SellOrder.objects.filter(
        status='PENDING',
        created_at__lte=timezone.now() - timedelta(minutes=10)
    ).count()

    return {
        'total_users': total_users,
        'total_balance': total_balance,
        'pending_deposits': pending_deposits,
        'pending_buys': pending_buys,
        'pending_withdrawals': pending_withdrawals,
        'pending_sells': pending_sells,
    }