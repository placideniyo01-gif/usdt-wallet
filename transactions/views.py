from django.shortcuts import render
from django.shortcuts import redirect
from core.models import SystemSettings
from .models import (
    Transaction,
    Deposit,
    BuyOrder,
    Withdrawal,
    SellOrder
)
from accounts.models import WalletUser
from decimal import Decimal
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404


def deposit_view(request):

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect('/')

    user = WalletUser.objects.get(
        id=user_id
    )

    settings = SystemSettings.objects.first()

    if request.method == "POST":

        amount = request.POST.get(
            "amount"
        )

        screenshot = request.FILES.get(
            "screenshot"
        )

        Deposit.objects.create(
            user=user,
            amount=amount,
            screenshot=screenshot,
            status='PENDING',
            visible_to_admin=False
        )

        editable_until = timezone.now() + timedelta(minutes=10)
        
        Transaction.objects.create(
            user=user,
            transaction_type="DEPOSIT",
            amount=amount,
            status="PENDING",
            description="Deposit request",
            editable_until=editable_until
        )

        messages.success(
            request,
            "Deposit submitted successfully."
        )

        return redirect('/dashboard/')

    return render(
        request,
        "transactions/deposit.html",
        {
            "settings": settings
        }
    )

def buy_view(request):

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect('/')

    user = WalletUser.objects.get(
        id=user_id
    )

    settings = SystemSettings.objects.first()

    rate = float(
        settings.usd_rwf_rate
    )

    rate = rate + (
        rate * 0.02
    )

    if request.method == "POST":

        amount = float(
            request.POST.get("amount")
        )

        screenshot = request.FILES.get(
            "screenshot"
        )

        rwf_amount = amount * rate

        BuyOrder.objects.create(
            user=user,
            amount=amount,
            screenshot=screenshot,
            status='PENDING',
            visible_to_admin=False
        )
        editable_until = timezone.now() + timedelta(minutes=10)
        
        Transaction.objects.create(
            user=user,
            transaction_type="BUY",
            amount=amount,
            rwf_amount=rwf_amount,
            status="PENDING",
            description="Buy request",
            editable_until=editable_until
        )

        return render(
            request,
            "transactions/buy_success.html"
        )

    return render(
        request,
        "transactions/buy.html",
        {
            "rate": rate,
            "settings": settings
        }
    )

def internal_transfer_view(request):

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect('/')

    sender = WalletUser.objects.get(
        id=user_id
    )

    if request.method == "POST":

        wallet_code = request.POST.get(
            "wallet_code"
        )

        amount = Decimal(
            request.POST.get("amount")
        )

        receiver = WalletUser.objects.filter(
            wallet_code=wallet_code
        ).first()

        if not receiver:

            messages.error(
                request,
                "Wallet code not found."
            )

            return redirect(
                '/internal-transfer/'
            )

        if receiver.id == sender.id:

            messages.error(
                request,
                "You cannot send to yourself."
            )

            return redirect(
                '/internal-transfer/'
            )

        if sender.balance < amount:

            messages.error(
                request,
                "Insufficient balance."
            )

            return redirect(
                '/internal-transfer/'
            )

        return render(
            request,
            "transactions/internal_confirm.html",
            {
                "wallet_code": receiver.wallet_code,
                "receiver_name": receiver.names,
                "amount": amount
            }
        )

    return render(
        request,
        "transactions/internal_transfer.html"
    )

def internal_confirm_view(request):

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect('/')

    sender = WalletUser.objects.get(
        id=user_id
    )

    if request.method == "POST":

        wallet_code = request.POST.get(
            "wallet_code"
        )

        amount = Decimal(
            request.POST.get(
                "amount"
            )
        )

        receiver = WalletUser.objects.get(
            wallet_code=wallet_code
        )

        if sender.balance < amount:

            messages.error(
                request,
                "Insufficient balance."
            )

            return redirect(
                '/dashboard/'
            )
        sender.balance -= amount
        sender.save()

        receiver.balance += amount
        receiver.save()

        Transaction.objects.create(
            user=sender,
            transaction_type="INTERNAL",
            amount=amount,
            receiver_wallet=wallet_code,
            status="APPROVED",
            description=f"Sent to {wallet_code}"
        )

        Transaction.objects.create(
            user=receiver,
            transaction_type="INTERNAL",
            amount=amount,
            receiver_wallet=sender.wallet_code,
            status="APPROVED",
            description=f"Received from {sender.wallet_code}"
        )

        messages.success(
            request,
            f'{amount} USDT sent successfully.'
        )

        return redirect(
            '/dashboard/'
        )

    return redirect(
        '/internal-transfer/'
    )

def history_view(request):

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect('/')

    user = WalletUser.objects.get(
        id=user_id
    )

    transactions = Transaction.objects.filter(
        user=user
    ).order_by(
        '-id'
    )

    return render(
        request,
        'transactions/history.html',
        {
            'transactions': transactions,
            'now': timezone.now()
        }
    )

def external_wallet_view(request):

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect('/')

    user = WalletUser.objects.get(
        id=user_id
    )

    if request.method == "POST":

        wallet_address = request.POST.get(
            "wallet_address"
        )

        amount = Decimal(
            request.POST.get("amount")
        )

        if amount < Decimal("10"):

            messages.error(
                request,
                "Minimum withdrawal is 10 USDT."
            )

            return redirect(
                '/external-wallet/'
            )

        if amount > Decimal("1000"):

            messages.error(
                request,
                "Maximum withdrawal is 1000 USDT per day."
            )

            return redirect(
                '/external-wallet/'
            )

        if amount <= 100:
            fee = Decimal("2")

        elif amount <= 300:
            fee = Decimal("3")

        elif amount <= 500:
            fee = Decimal("4")

        else:
            fee = Decimal("5")

        total_required = amount + fee

        if user.balance < total_required:

            messages.error(
                request,
                f'You need {total_required} USDT including fee.'
            )

            return redirect(
                '/external-wallet/'
            )

        request.session[
            'external_wallet_address'
        ] = wallet_address

        request.session[
            'external_amount'
        ] = str(amount)

        request.session[
            'external_fee'
        ] = str(fee)

        return redirect(
            '/external-confirm/'
        )

    return render(
        request,
        'transactions/external_wallet.html'
    )

def external_confirm_view(request):

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect('/')

    user = WalletUser.objects.get(
        id=user_id
    )

    wallet_address = request.session.get(
        'external_wallet_address'
    )

    amount = request.session.get(
        'external_amount'
    )

    fee = request.session.get(
        'external_fee'
    )

    if request.method == "POST":

        withdrawal.objects.create(
            user=user,
            amount=amount,
            screenshot=screenshot,
            status='PENDING',
            visible_to_admin=False
        )

        editable_until = timezone.now() + timedelta(minutes=10)
        
        Transaction.objects.create(
            user=user,
            transaction_type="EXTERNAL",
            amount=amount,
            fee=fee,
            status="PENDING",
            receiver_wallet=wallet_address,
            description=f"Withdrawal to {wallet_address}",
            editable_until=editable_until
        )

        request.session.pop(
            'external_wallet_address',
            None
        )

        request.session.pop(
            'external_amount',
            None
        )

        request.session.pop(
            'external_fee',
            None
        )

        messages.success(
            request,
            "Withdrawal request submitted."
        )

        return redirect(
            '/dashboard/'
        )

    return render(
        request,
        'transactions/external_confirm.html',
        {
            'wallet_address': wallet_address,
            'amount': amount,
            'fee': fee
        }
    )

def sell_view(request):
    edit_tx = None

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect('/')

    user = WalletUser.objects.get(
        id=user_id
    )

    settings = SystemSettings.objects.first()

    rate = Decimal(
        settings.usd_rwf_rate
    )

    sell_rate = rate - (
        rate * Decimal("0.02")
    )

    if request.method == "POST":

        print(request.POST)

        amount_value = request.POST.get(
            "amount"
        )

        if not amount_value:

            messages.error(
                request,
                "Please enter amount."
            )

            return redirect(
                '/sell/'
            )

        amount = Decimal(
            amount_value
        )

        phone = request.POST.get(
            "phone"
        )

        receiver_name = request.POST.get(
            "receiver_name"
        )

        if user.balance < amount:

            messages.error(
                request,
                "Insufficient balance."
            )

            return redirect(
                '/sell/'
            )

        rwf_amount = (
            amount * sell_rate
        )

        SellOrder.objects.create(
            user=user,
            amount=amount,
            screenshot=screenshot,
            status='PENDING',
            visible_to_admin=False
        )

        editable_until = timezone.now() + timedelta(minutes=10)
        
        Transaction.objects.create(
            user=user,
            transaction_type="SELL",
            amount=amount,
            rwf_amount=rwf_amount,
            status="PENDING",
            description=f"Sell to {phone}",
            editable_until=editable_until
        )

        messages.success(
            request,
            "Sell request submitted."
        )

        edit_tx = None

        edit_id = request.session.get(
            "edit_tx_id"
        )

        return redirect(
            '/dashboard/'
        )

        if edit_id:

            edit_tx = Transaction.objects.filter(
                id=edit_id,
                user=user,
                transaction_type="SELL"
            ).first()

    return render(
        request,
        "transactions/sell.html",
        {
            "user": user,
            'rate': sell_rate,
            "edit_tx": edit_tx
        }
    )

def cancel_transaction_view(request, pk):

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect('/')

    transaction = get_object_or_404(
        Transaction,
        id=pk,
        user_id=user_id,
        status='PENDING'
    )

    if transaction.transaction_type == "DEPOSIT":

        Deposit.objects.filter(
            user_id=user_id,
            amount=transaction.amount,
            status='PENDING'
        ).update(
            status='CANCELLED',
            processed=True
        )

    elif transaction.transaction_type == "BUY":

        BuyOrder.objects.filter(
            user_id=user_id,
            amount=transaction.amount,
            status='PENDING'
        ).update(
            status='CANCELLED',
            processed=True
        )

    elif transaction.transaction_type == "SELL":

        SellOrder.objects.filter(
            user_id=user_id,
            amount=transaction.amount,
            status='PENDING'
        ).update(
            status='CANCELLED',
            processed=True
        )

    elif transaction.transaction_type == "EXTERNAL":

        Withdrawal.objects.filter(
            user_id=user_id,
            amount=transaction.amount,
            status='PENDING'
        ).update(
            status='CANCELLED',
            processed=True
        )

    transaction.status = 'CANCELLED'
    transaction.save()

    messages.success(
        request,
        "Transaction cancelled successfully."
    )

    return redirect('history')