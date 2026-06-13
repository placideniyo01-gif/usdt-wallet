from django.db import models


class SystemSettings(models.Model):

    company_name = models.CharField(
        max_length=100,
        default="USDT Wallet"
    )

    trc20_wallet = models.CharField(
        max_length=255
    )

    usd_rwf_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1500
    )

    mtn_code = models.CharField(
        max_length=20,
        default="1861343"
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.company_name