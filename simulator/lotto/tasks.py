import random
import time

from celery import states
from django.db import transaction

from config import celery_app  # noqa

from .models import LottoCoupon, LottoGame


def generate_random_numbers():
    return random.sample(range(1, 50), 6)


@celery_app.task(bind=True)
def bulk_create_coupons(self, user_id, game_id, quantity):
    batch_size = 3000
    processed_coupons = 0

    for offset in range(0, quantity, batch_size):
        user_numbers_list = []
        end_index = min(offset + batch_size, quantity)

        for _ in range(offset, end_index):
            numbers = generate_random_numbers()
            user_numbers_list.append(
                LottoCoupon(
                    user_id=user_id,
                    game_id=game_id,
                    numbers=numbers,
                )
            )
            processed_coupons += 1

        with transaction.atomic():
            LottoCoupon.objects.bulk_create(user_numbers_list)

            data = {
                "game_id": game_id,
                "type": "Generating coupons",
                "progress": round((processed_coupons / quantity) * 100, 2),
                "processed_coupons": offset,
                "total_coupons": quantity,
            }

            self.update_state(
                state=states.STARTED,
                meta=data,
            )

            time.sleep(0.05)

    data = {
        "game_id": game_id,
        "type": "Generating coupons",
        "progress": 100,
        "processed_coupons": quantity,
        "total_coupons": quantity,
    }

    return data


@celery_app.task(bind=True)
def bulk_update_coupons_status(self, game_id):
    self.update_state(state=states.STARTED, meta={"game_id": game_id})
    batch_size = 5000

    game = LottoGame.objects.filter(id=game_id).values("id", "numbers").first()

    if not game:
        return f"Game with id {game_id} does not exist."

    winning_set = set(game["numbers"])

    coupons = LottoCoupon.objects.filter(game_id=game_id).values("id", "numbers", "status")

    total_coupons = coupons.count()
    processed_coupons = 0

    coupons_updates = []
    for coupon in coupons:
        hit_count = len(winning_set.intersection(set(coupon["numbers"])))
        coupon_update = LottoCoupon(id=coupon["id"], status=str(hit_count))
        coupons_updates.append(coupon_update)

        processed_coupons += 1

        if len(coupons_updates) % batch_size == 0:
            perform_bulk_update(coupons_updates)
            coupons_updates = []

            # Send status update to the user
            data = {
                "game_id": game_id,
                "type": "Evaluating coupons",
                "progress": round(processed_coupons / total_coupons, 2) * 100,
                "processed_coupons": processed_coupons,
                "total_coupons": total_coupons,
            }
            self.update_state(
                state=states.STARTED,
                meta=data,
            )
    if coupons_updates:
        perform_bulk_update(coupons_updates)

    data = {
        "game_id": game_id,
        "type": "Evaluating coupons",
        "progress": 100,
        "processed_coupons": processed_coupons,
        "total_coupons": total_coupons,
    }

    return data


def perform_bulk_update(coupons_updates):
    with transaction.atomic():
        LottoCoupon.objects.bulk_update(coupons_updates, ["status"])
