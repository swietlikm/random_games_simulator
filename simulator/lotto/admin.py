from django.contrib import admin

from .models import LottoCoupon, LottoGame

admin.site.register(LottoGame)


@admin.register(LottoCoupon)
class UserNumbersAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "game",
        "status",
    )
    list_filter = ("game__date", "status")
    search_fields = ("status",)
    sortable_by = ("status",)
