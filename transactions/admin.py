from django.contrib import admin
from .models import (
    Deposit,
    BuyOrder,
    Withdrawal,
    SellOrder,
    Transaction
)

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'amount',
        'status',
        'created_at'
    )

    list_editable = (
        'status',
    )

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        if change:

            tx = Transaction.objects.filter(
                user=obj.user,
                transaction_type='DEPOSIT',
                amount=obj.amount
            ).order_by('-created_at').first()

            if tx and tx.status == "CANCELLED":
                obj.status = "CANCELLED"
                obj.processed = True

                super().save_model(
                    request,
                    obj,
                    form,
                    change
                )
                return
            old = Deposit.objects.get(
                pk=obj.pk
            )

            if (
                not obj.processed
                and
                old.status != 'APPROVED'
                and
                obj.status == 'APPROVED'
            ):

                obj.user.balance += obj.amount
                obj.user.save()
                obj.processed = True

                Transaction.objects.filter(
                    user=obj.user,
                    transaction_type='DEPOSIT',
                    amount=obj.amount,
                    status='PENDING'
                ).update(
                    status='APPROVED'
                )

        super().save_model(
            request,
            obj,
            form,
            change
        )

@admin.register(BuyOrder)
class BuyOrderAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'amount',
        'rwf_amount',
        'status',
        'created_at'
    )

    list_editable = (
        'status',
    )

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        if change:

            tx = Transaction.objects.filter(
                user=obj.user,
                transaction_type='BUY',
                amount=obj.amount
            ).order_by('-created_at').first()

            if tx and tx.status == "CANCELLED":
                obj.status = "CANCELLED"
                obj.processed = True

                super().save_model(
                    request,
                    obj,
                    form,
                    change
                )
                return
            old = BuyOrder.objects.get(
                pk=obj.pk
            )

            if (
                not obj.processed
                and
                old.status != 'APPROVED'
                and
                obj.status == 'APPROVED'
            ):

                obj.user.balance += obj.amount
                obj.user.save()
                obj.processed = True

                Transaction.objects.filter(
                    user=obj.user,
                    transaction_type='BUY',
                    amount=obj.amount,
                    status='PENDING'
                ).update(
                    status='APPROVED'
                )

        super().save_model(
            request,
            obj,
            form,
            change
        )

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'amount',
        'fee',
        'wallet_address',
        'status',
        'created_at'
    )

    list_editable = (
        'status',
    )

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        if change:

            tx = Transaction.objects.filter(
                user=obj.user,
                transaction_type='WITHDRAWAL',
                amount=obj.amount
            ).order_by('-created_at').first()

            if tx and tx.status == "CANCELLED":
                obj.status = "CANCELLED"
                obj.processed = True

                super().save_model(
                    request,
                    obj,
                    form,
                    change
                )
                return
            old = Withdrawal.objects.get(
                pk=obj.pk
            )

            if (
                not obj.processed
                and
                old.status != 'APPROVED'
                and
                obj.status == 'APPROVED'
            ):

                total = (
                    obj.amount +
                    obj.fee
                )

                obj.user.balance -= total
                obj.user.save()
                obj.processed = True

                Transaction.objects.filter(
                    user=obj.user,
                    transaction_type='EXTERNAL',
                    amount=obj.amount,
                    status='PENDING'
                ).update(
                    status='APPROVED'
                )

        super().save_model(
            request,
            obj,
            form,
            change
        )

@admin.register(SellOrder)
class SellOrderAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'amount',
        'rwf_amount',
        'phone_number',
        'receiver_name',
        'status',
        'created_at'
    )

    list_editable = (
        'status',
    )

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        if change:

            tx = Transaction.objects.filter(
                user=obj.user,
                transaction_type='SELL',
                amount=obj.amount
            ).order_by('-created_at').first()

            if tx and tx.status == "CANCELLED":
                obj.status = "CANCELLED"
                obj.processed = True

                super().save_model(
                    request,
                    obj,
                    form,
                    change
                )
                return
            old = SellOrder.objects.get(
                pk=obj.pk
            )

            if (
                not obj.processed
                and
                old.status != 'APPROVED'
                and
                obj.status == 'APPROVED'
            ):

                obj.user.balance -= obj.amount
                obj.user.save()
                obj.processed = True

                Transaction.objects.filter(
                    user=obj.user,
                    transaction_type='SELL',
                    amount=obj.amount,
                    status='PENDING'
                ).update(
                    status='APPROVED'
                )

        super().save_model(
            request,
            obj,
            form,
            change
        )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'transaction_type',
        'amount',
        'status',
        'created_at'
    )

    list_filter = (
        'transaction_type',
        'status'
    )

    search_fields = (
        'user__wallet_code',
        'user__names'
    )
