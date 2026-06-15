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
from django.contrib.auth.hashers import check_password


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

        editable_until = timezone.now() + timedelta(minutes=10)

        tx = Transaction.objects.create(
            user=user,
            transaction_type="DEPOSIT",
            amount=amount,
            status="PENDING",
            description="Deposit request",
            editable_until=editable_until
        )

        Deposit.objects.create(
            user=user,
            amount=amount,
            screenshot=screenshot,
            status="PENDING",
            visible_to_admin=False,
            transaction=tx
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

    user_id = request.session.get("wallet_user_id")

    if not user_id:
        return redirect('/')

    user = WalletUser.objects.get(id=user_id)

    settings = SystemSettings.objects.first()

    rate = Decimal(str(settings.usd_rwf_rate))
    rate = rate + (rate * Decimal("0.02"))

    if request.method == "POST":

        amount = Decimal(request.POST.get("amount"))

        screenshot = request.FILES.get("screenshot")

        rwf_amount = amount * rate

        editable_until = timezone.now() + timedelta(minutes=10)

        tx = Transaction.objects.create(
            user=user,
            transaction_type="BUY",
            amount=amount,
            rwf_amount=rwf_amount,
            status="PENDING",
            description="Buy request",
            editable_until=editable_until
        )

        BuyOrder.objects.create(
            user=user,
            amount=amount,
            rwf_amount=rwf_amount,
            screenshot=screenshot,
            status="PENDING",
            visible_to_admin=False,
            transaction=tx
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

        if sender.available_balance < amount:

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

        secret_code = request.POST.get(
            "secret_code"
        )

        if not check_password(
            secret_code,
            sender.secret_code
        ):

            messages.error(
                request,
                "Invalid secret code."
            )

            return redirect(
                "/internal-transfer/"
            )

        if sender.available_balance < amount:

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

        if user.available_balance < total_required:

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

        secret_code = request.POST.get(
            "secret_code"
        )

        if not check_password(
            secret_code,
            user.secret_code
        ):

            messages.error(
                request,
                "Invalid secret code."
            )

            return redirect(
                "/external-confirm/"
            )

        editable_until = (
            timezone.now() +
            timedelta(minutes=10)
        )

        tx = Transaction.objects.create(
            user=user,
            transaction_type="EXTERNAL",
            amount=amount,
            fee=fee,
            status="PENDING",
            receiver_wallet=wallet_address,
            description=f"Withdrawal to {wallet_address}",
            editable_until=editable_until
        )

        Withdrawal.objects.create(
            user=user,
            wallet_address=wallet_address,
            amount=amount,
            fee=fee,
            status='PENDING',
            visible_to_admin=False,
            transaction=tx
        )

        user.locked_balance += (
            Decimal(amount) +
            Decimal(fee)
        )

        user.save()

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

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect("/")

    user = WalletUser.objects.get(
        id=user_id
    )

    settings = SystemSettings.objects.first()

    rate = Decimal(
        str(settings.usd_rwf_rate)
    )

    sell_rate = rate - (
        rate * Decimal("0.02")
    )

    edit_tx = None

    if request.method == "POST":

        amount_value = request.POST.get(
            "amount"
        )

        if not amount_value:

            messages.error(
                request,
                "Please enter amount."
            )

            return redirect(
                "/sell/"
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

        secret_code = request.POST.get(
            "secret_code"
        )

        if not check_password(
            secret_code,
            user.secret_code
        ):

            messages.error(
                request,
                "Invalid secret code."
            )

            return redirect(
                "/sell/"
            )

        if user.available_balance < amount:

            messages.error(
                request,
                "Insufficient available balance."
            )

            return redirect(
                "/sell/"
            )

        rwf_amount = (
            amount * sell_rate
        )

        editable_until = (
            timezone.now() +
            timedelta(minutes=10)
        )

        tx = Transaction.objects.create(
            user=user,
            transaction_type="SELL",
            amount=amount,
            rwf_amount=rwf_amount,
            status="PENDING",
            description=f"Sell to {phone}",
            editable_until=editable_until
        )

        SellOrder.objects.create(
            user=user,
            amount=amount,
            rwf_amount=rwf_amount,
            phone_number=phone,
            receiver_name=receiver_name,
            status="PENDING",
            visible_to_admin=False,
            transaction=tx
        )

        user.locked_balance += amount
        user.save()

        messages.success(
            request,
            "Sell request submitted successfully."
        )

        return redirect(
            "/dashboard/"
        )

    return render(
        request,
        "transactions/sell.html",
        {
            "user": user,
            "rate": sell_rate,
            "edit_tx": edit_tx
        }
    )

def cancel_transaction_view(request, pk):

    print("CANCEL VIEW HIT")
    print("METHOD =", request.method)
    print("TX =", pk)

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect("/")

    transaction = get_object_or_404(
        Transaction,
        id=pk,
        user_id=user_id,
        status="PENDING"
    )

    user = transaction.user

    if transaction.transaction_type == "DEPOSIT":

        Deposit.objects.filter(
            user_id=user_id,
            amount=transaction.amount,
            status="PENDING"
        ).update(
            status="CANCELLED",
            processed=True
        )

    elif transaction.transaction_type == "BUY":

        BuyOrder.objects.filter(
            user_id=user_id,
            amount=transaction.amount,
            status="PENDING"
        ).update(
            status="CANCELLED",
            processed=True
        )

    elif transaction.transaction_type == "SELL":

        sell_order = SellOrder.objects.filter(
            transaction=transaction
        ).first()

        if sell_order:
            sell_order.status = "CANCELLED"
            sell_order.processed = True
            sell_order.save()

        user.locked_balance -= transaction.amount

        print("AMOUNT:", transaction.amount)
        print("AFTER:", user.locked_balance)

        if user.locked_balance < 0:
            user.locked_balance = 0

        user.save()

    elif transaction.transaction_type == "EXTERNAL":

        print("BEFORE:", user.locked_balance)

        withdrawal = Withdrawal.objects.filter(
            transaction=transaction
        ).first()

        if withdrawal:
            withdrawal.status = "CANCELLED"
            withdrawal.processed = True
            withdrawal.save()

        amount_to_unlock = transaction.amount

        if transaction.fee:
            amount_to_unlock += transaction.fee

        print("UNLOCK:", amount_to_unlock)

        user.locked_balance -= amount_to_unlock

        print("AFTER:", user.locked_balance)

        if user.locked_balance < 0:
            user.locked_balance = 0

        user.save()

    transaction.status = "CANCELLED"
    transaction.save()

    messages.success(
        request,
        "Transaction cancelled successfully."
    )
    print("CANCEL COMPLETED")

    return redirect("history")