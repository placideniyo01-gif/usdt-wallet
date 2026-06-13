from django.db import models


class WalletUser(models.Model):

    names = models.CharField(max_length=200)

    phone_number = models.CharField(
        max_length=20,
        unique=True
    )

    wallet_code = models.CharField(
        max_length=20,
        unique=True
    )

    secret_code = models.CharField(
        max_length=255
    )

    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.wallet_code