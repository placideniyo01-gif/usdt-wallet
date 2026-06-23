from django.db import models
from accounts.models import WalletUser
from django.utils import timezone
from datetime import timedelta

class Transaction(models.Model):

    STATUS = (
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('REJECTED', 'REJECTED'),
        ('CANCELLED','CANCELLED'),
    )

    TYPES = (
        ('DEPOSIT', 'DEPOSIT'),
        ('BUY', 'BUY'),
        ('SELL', 'SELL'),
        ('INTERNAL', 'INTERNAL'),
        ('EXTERNAL', 'EXTERNAL'),
        ('INTERNSHIP', 'INTERNSHIP'),
    )

    user = models.ForeignKey(
        WalletUser,
        on_delete=models.CASCADE
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TYPES
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    fee = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    rwf_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='PENDING'
    )

    screenshot = models.ImageField(
        upload_to='proofs/',
        blank=True,
        null=True
    )

    receiver_wallet = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    reference = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    editable_until = models.DateTimeField(
        null=True,
        blank=True
    )

    visible_to_admin_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.transaction_type

class Deposit(models.Model):

    STATUS = (
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('REJECTED', 'REJECTED'),
        ('CANCELLED','CANCELLED'),
    )

    user = models.ForeignKey(
        WalletUser,
        on_delete=models.CASCADE
    )

    editable_until = models.DateTimeField(
        null=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    screenshot = models.ImageField(
        upload_to='proofs/'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='PENDING'
    )

    processed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    visible_to_admin = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"Deposit {self.user}"

class BuyOrder(models.Model):

    STATUS = (
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('REJECTED', 'REJECTED'),
        ('CANCELLED','CANCELLED'),
    )

    user = models.ForeignKey(
        WalletUser,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    rwf_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    editable_until = models.DateTimeField(
        null=True,
        blank=True
    )

    screenshot = models.ImageField(
        upload_to='proofs/'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='PENDING'
    )

    processed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    visible_to_admin = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"Buy {self.user}"

class Withdrawal(models.Model):

    STATUS = (
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('REJECTED', 'REJECTED'),
        ('CANCELLED','CANCELLED'),
    )

    user = models.ForeignKey(
        WalletUser,
        on_delete=models.CASCADE
    )

    wallet_address = models.CharField(
        max_length=200
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    editable_until = models.DateTimeField(
        null=True,
        blank=True
    )

    fee = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='PENDING'
    )

    processed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    visible_to_admin = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"Withdrawal {self.user}"

class SellOrder(models.Model):

    STATUS = (
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('REJECTED', 'REJECTED'),
        ('CANCELLED','CANCELLED'),
    )

    user = models.ForeignKey(
        WalletUser,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    editable_until = models.DateTimeField(
        null=True,
        blank=True
    )

    rwf_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2
    )

    phone_number = models.CharField(
        max_length=20
    )

    receiver_name = models.CharField(
        max_length=200
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='PENDING'
    )

    processed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    visible_to_admin = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"Sell {self.user}"

class InternshipTransfer(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    )

    user = models.ForeignKey(
        "accounts.WalletUser",
        on_delete=models.CASCADE
    )

    receiver_username = models.CharField(
        max_length=150
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SUCCESS"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.wallet_code} -> {self.receiver_username}"