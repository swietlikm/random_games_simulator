import time

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class LottoGame(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
    ]

    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="OPEN")

    numbers = models.JSONField(blank=True, null=True)

    n1 = models.SmallIntegerField(blank=True, null=True)
    n2 = models.SmallIntegerField(blank=True, null=True)
    n3 = models.SmallIntegerField(blank=True, null=True)
    n4 = models.SmallIntegerField(blank=True, null=True)
    n5 = models.SmallIntegerField(blank=True, null=True)
    n6 = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Game {self.id} - {self.date} ({self.status.title()})"

    @property
    def user_coupons(self):
        return self.usernumbers.filter(game=self).count()

    from django.db.models import F

    def save(self, *args, **kwargs):
        start_time = time.time()  # Record the start time

        if self.numbers is not None and all(getattr(self, f"n{i}") is not None for i in range(1, 7)):
            self.status = "closed"

            hit_number_set = {getattr(self, f"n{i}") for i in range(1, 7) if getattr(self, f"n{i}") is not None}

            # Store attribute values in variables to avoid redundant attribute access
            usernumbers = self.usernumbers.all()
            usernumber_values = list(usernumber.values() for usernumber in usernumbers)

            # Check and update user numbers status in bulk
            for i, usernumber in enumerate(usernumbers):
                user_number_set = set(usernumber_values[i]["numbers"])

                # Count the intersection of hit numbers and user numbers
                hit_count = len(user_number_set.intersection(hit_number_set))
                if usernumber_values[i]["status"] != str(hit_count):
                    usernumbers[i].status = str(hit_count)

            # Bulk update user numbers only if there are changes
            self.usernumbers.bulk_update(usernumbers, ["status"])

        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time
        print(f"Execution Time: {execution_time} seconds")

        # Only call the superclass save method if there are changes
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Lotto game")
        verbose_name_plural = _("Lotto games")
        ordering = ["-date"]


class UserNumbers(models.Model):
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usernumbers")
    game = models.ForeignKey(LottoGame, on_delete=models.CASCADE, related_name="usernumbers")
    status = models.CharField(choices=LOTTO_STATUSES, default="OPEN", max_length=10)
    numbers = models.JSONField(blank=True, null=True)

    n1 = models.SmallIntegerField(blank=True, null=True)
    n2 = models.SmallIntegerField(blank=True, null=True)
    n3 = models.SmallIntegerField(blank=True, null=True)
    n4 = models.SmallIntegerField(blank=True, null=True)
    n5 = models.SmallIntegerField(blank=True, null=True)
    n6 = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Numbers for Game {self.game_id}"

    class Meta:
        verbose_name = _("User numbers")
        verbose_name_plural = _("User numbers")
