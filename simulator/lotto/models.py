from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AbstractGame(models.Model):
    STATUS_CHOICES = [
        ("OPEN", _("Open")),
        ("CLOSED", _("Closed")),
    ]

    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="OPEN")
    objects = models.Manager()

    def __str__(self):
        return f"{self.__class__.__name__} {self.id} - {self.date} ({self.status})"

    class Meta:
        abstract = True


class LottoGame(AbstractGame):
    numbers = models.JSONField(blank=True, null=True)

    @property
    def user_coupons(self):
        return self.lottocoupons.count()

    class Meta:
        verbose_name = _("Lotto game")
        verbose_name_plural = _("Lotto games")
        ordering = ["-date"]


class LottoCoupon(models.Model):
    LOTTO_STATUSES = (
        ("6", "6"),
        ("5", "5"),
        ("4", "4"),
        ("3", "3"),
        ("2", "2"),
        ("1", "1"),
        ("0", "0"),
        ("OPEN", "Open"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lottocoupons")
    game = models.ForeignKey(LottoGame, on_delete=models.CASCADE, related_name="lottocoupons")
    status = models.CharField(choices=LOTTO_STATUSES, default="OPEN", max_length=10)
    numbers = models.JSONField()

    objects = models.Manager()

    def __str__(self):
        return f"{self.user.username}'s Lotto numbers for Game id: {self.game_id}"

    class Meta:
        verbose_name = _("Lotto coupon")
        verbose_name_plural = _("Lotto coupons")
