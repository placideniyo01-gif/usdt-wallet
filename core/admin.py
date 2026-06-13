from django.contrib import admin
from .models import SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'usd_rwf_rate',
        'mtn_code',
        'trc20_wallet'
    )