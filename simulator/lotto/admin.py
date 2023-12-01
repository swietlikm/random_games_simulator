from django.contrib import admin

from .models import LottoGame, UserNumbers

admin.site.register(LottoGame)


@admin.register(UserNumbers)
class UserNumbersAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "game",
        "status",
    )
    list_filter = ("game__date", "status")
    search_fields = ("status",)
    sortable_by = ("status",)
