from django.shortcuts import render
from django.db.models import Sum
from accounts.models import WalletUser
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from transactions.models import (
    Transaction,
    Deposit,
    BuyOrder,
    Withdrawal,
    SellOrder
)
from django.utils import timezone
from datetime import timedelta

@staff_member_required
def admin_dashboard(request):

    wallet = request.GET.get(
        "wallet",
        ""
    )

    pending_only = request.GET.get(
        "pending_only",
        ""
    )

    deposits = Deposit.objects.filter(
        status="PENDING",
        created_at__lte=timezone.now() - timedelta(minutes=10)
    )

    buys = BuyOrder.objects.filter(
        status="PENDING",
        created_at__lte=timezone.now() - timedelta(minutes=10)
    )

    withdrawals = Withdrawal.objects.filter(
        status="PENDING",
        created_at__lte=timezone.now() - timedelta(minutes=10)
    )

    sells = SellOrder.objects.filter(
        status="PENDING",
        created_at__lte=timezone.now() - timedelta(minutes=10)
    )

    if wallet:

        deposits = deposits.filter(
            user__wallet_code__icontains=wallet
        )

        buys = buys.filter(
            user__wallet_code__icontains=wallet
        )

        withdrawals = withdrawals.filter(
            user__wallet_code__icontains=wallet
        )

        sells = sells.filter(
            user__wallet_code__icontains=wallet
        )

    if pending_only == "1":

        deposits = deposits.filter(
            status="PENDING"
        )

        buys = buys.filter(
            status="PENDING"
        )

        withdrawals = withdrawals.filter(
            status="PENDING"
        )

        sells = sells.filter(
            status="PENDING"
        )

    context = {

        "total_users":
        WalletUser.objects.count(),

        "total_balance":
        WalletUser.objects.aggregate(
            Sum("balance")
        )["balance__sum"] or 0,

        "pending_deposits":
        deposits.order_by(
            "-id"
        ),

        "pending_buys":
        buys.order_by(
            "-id"
        ),

        "pending_withdrawals":
        withdrawals.order_by(
            "-id"
        ),

        "pending_sells":
        sells.order_by(
            "-id"
        ),

        "search_wallet":
        wallet,

        "pending_only":
        pending_only,
    }

    return render(
        request,
        "admin_dashboard.html",
        context
    )

@staff_member_required
def update_deposit_status(request):

    if request.method == "POST":

        ids = request.POST.getlist(
            "deposit_ids"
        )

        for deposit_id in ids:

            deposit = Deposit.objects.get(
                id=deposit_id
            )

            new_status = request.POST.get(
                f"status_{deposit_id}"
            )

            if (
                new_status == "APPROVED"
                and
                deposit.status != "APPROVED"
            ):

                deposit.user.balance += deposit.amount
                deposit.user.save()

            deposit.status = new_status
            deposit.save()

            Transaction.objects.filter(
                user=deposit.user,
                transaction_type="DEPOSIT",
                amount=deposit.amount,
                status="PENDING"
            ).update(
                status=new_status
            )

    return redirect(
        "/admin-dashboard/"
    )


@staff_member_required
def update_buy_status(request):

    if request.method == "POST":

        ids = request.POST.getlist(
            "buy_ids"
        )

        for buy_id in ids:

            buy = BuyOrder.objects.get(
                id=buy_id
            )

            new_status = request.POST.get(
                f"status_{buy_id}"
            )

            if (
                new_status == "APPROVED"
                and
                not buy.processed
            ):

                buy.user.balance += buy.amount
                buy.user.save()

                buy.processed = True

            buy.status = new_status
            buy.save()

            Transaction.objects.filter(
                user=buy.user,
                transaction_type="BUY",
                amount=buy.amount,
                status="PENDING"
            ).update(
                status=new_status
            )

    return redirect(
        "/admin-dashboard/"
    )


@staff_member_required
def update_withdrawal_status(request):

    if request.method == "POST":

        ids = request.POST.getlist(
            "withdrawal_ids"
        )

        for withdrawal_id in ids:

            withdrawal = Withdrawal.objects.get(
                id=withdrawal_id
            )

            new_status = request.POST.get(
                f"status_{withdrawal_id}"
            )

            if (
                new_status == "APPROVED"
                and
                not withdrawal.processed
            ):

                total = (
                    withdrawal.amount +
                    withdrawal.fee
                )

                withdrawal.user.balance -= total
                withdrawal.user.save()

                withdrawal.processed = True

            withdrawal.status = new_status
            withdrawal.save()

            Transaction.objects.filter(
                user=withdrawal.user,
                transaction_type="EXTERNAL",
                amount=withdrawal.amount,
                status="PENDING"
            ).update(
                status=new_status
            )

    return redirect(
        "/admin-dashboard/"
    )


@staff_member_required
def update_sell_status(request):

    if request.method == "POST":

        ids = request.POST.getlist(
            "sell_ids"
        )

        for sell_id in ids:

            sell = SellOrder.objects.get(
                id=sell_id
            )

            new_status = request.POST.get(
                f"status_{sell_id}"
            )

            if (
                new_status == "APPROVED"
                and
                not sell.processed
            ):

                sell.user.balance -= sell.amount
                sell.user.save()

                sell.processed = True

            sell.status = new_status
            sell.save()

            Transaction.objects.filter(
                user=sell.user,
                transaction_type="SELL",
                amount=sell.amount,
                status="PENDING"
            ).update(
                status=new_status
            )

    return redirect(
        "/admin-dashboard/"
    )