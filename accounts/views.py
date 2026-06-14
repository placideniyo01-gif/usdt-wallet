import secrets
import string
from transactions.models import Transaction
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib import messages
from .models import WalletUser


def generate_wallet_code():

    characters = string.ascii_uppercase + string.digits

    while True:

        code = ''.join(
            secrets.choice(characters)
            for _ in range(20)
        )

        exists = WalletUser.objects.filter(
            wallet_code=code
        ).exists()

        if not exists:
            return code

def register_view(request):

    if request.method == "POST":

        names = request.POST.get("names")
        phone = request.POST.get("phone")
        secret = request.POST.get("secret")

        wallet_code = generate_wallet_code()

        WalletUser.objects.create(
            names=names,
            phone_number=phone,
            wallet_code=wallet_code,
            secret_code=make_password(secret)
        )

        return render(
            request,
            "accounts/wallet_created.html",
            {
                "wallet_code": wallet_code
            }
        )

    return render(
        request,
        "accounts/register.html"
    )

def login_view(request):

    if request.method == "POST":

        wallet_code = request.POST.get(
            "wallet_code"
        )

        user = WalletUser.objects.filter(
            wallet_code=wallet_code
        ).first()

        if user:

            request.session[
                "wallet_user_id"
            ] = user.id

            return redirect(
                "/dashboard/"
            )

    return render(
        request,
        "accounts/login.html"
    )

def dashboard_view(request):

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
        '-created_at'
    )[:10]

    Deposit.objects.filter(
        visible_to_admin=False,
        status='PENDING',
        created_at__lte=timezone.now() - timedelta(minutes=10)
    ).update(
        visible_to_admin=True
    )

    BuyOrder.objects.filter(
        visible_to_admin=False,
        status='PENDING',
        created_at__lte=timezone.now() - timedelta(minutes=10)
    ).update(
        visible_to_admin=True
    )

    Withdrawal.objects.filter(
        visible_to_admin=False,
        status='PENDING',
        created_at__lte=timezone.now() - timedelta(minutes=10)
    ).update(
        visible_to_admin=True
    )

    SellOrder.objects.filter(
        visible_to_admin=False,
        status='PENDING',
        created_at__lte=timezone.now() - timedelta(minutes=10)
    ).update(
        visible_to_admin=True
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "user": user,
            "transactions": transactions,
            "now": timezone.now()
        }
    )
def logout_view(request):

    request.session.flush()

    return redirect('/')

from django.shortcuts import redirect, get_object_or_404

def cancel_transaction(request, id):

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect("/")

    tx = get_object_or_404(
        Transaction,
        id=id
    )

    if tx.user.id != user_id:

        messages.error(
            request,
            "Unauthorized action."
        )

        return redirect("/dashboard/")

    if tx.status != "PENDING":

        messages.error(
            request,
            "Only pending transactions can be cancelled."
        )

        return redirect("/dashboard/")

    if (
        tx.editable_until
        and
        timezone.now() > tx.editable_until
    ):

        messages.error(
            request,
            "Transaction can no longer be cancelled."
        )

        return redirect("/dashboard/")

    tx.status = "CANCELLED"
    tx.save()

    messages.success(
        request,
        "Transaction cancelled successfully."
    )

    return redirect("/history/")

from django.shortcuts import get_object_or_404
from transactions.models import (
    Transaction,
    Deposit,
    BuyOrder,
    Withdrawal,
    SellOrder
)

from django.shortcuts import get_object_or_404, redirect

def edit_transaction_view(request, pk):
    transaction = get_object_or_404(Transaction, id=pk)

    if transaction.transaction_type == "DEPOSIT":
        return redirect('deposit')

    elif transaction.transaction_type == "BUY":
        return redirect('buy')

    elif transaction.transaction_type == "SELL":
        return redirect('sell')

    elif transaction.transaction_type == "EXTERNAL":
        return redirect('external_wallet')  # niba iri zina rya URL

    elif transaction.transaction_type == "INTERNAL":
        return redirect('internal_transfer')

    return redirect('history')

from django.shortcuts import get_object_or_404

def cancel_transaction_view(request, pk):

    user_id = request.session.get(
        "wallet_user_id"
    )

    if not user_id:
        return redirect('/')

    tx = get_object_or_404(
        Transaction,
        id=pk,
        user_id=user_id,
        status='PENDING'
    )

    if tx.editable_until and timezone.now() <= tx.editable_until:

        tx.status = 'CANCELLED'
        tx.save()

        messages.success(
            request,
            "Transaction cancelled successfully."
        )

    else:

        messages.error(
            request,
            "Cancellation period expired."
        )

    return redirect('/dashboard/')

from django.shortcuts import render
from django.contrib import messages
from accounts.models import WalletUser


def forgot_wallet_view(request):

    wallet_code = None

    if request.method == "POST":

        names = request.POST.get("names")
        phone = request.POST.get("phone_number")
        secret_code = request.POST.get("secret_code")

        user = WalletUser.objects.filter(
            names=names,
            phone_number=phone,
            secret_code=secret_code
        ).first()

        if user:
            wallet_code = user.wallet_code
        else:
            messages.error(
                request,
                "Information provided is incorrect."
            )

    return render(
        request,
        "accounts/forgot_wallet.html",
        {
            "wallet_code": wallet_code
        }
    )