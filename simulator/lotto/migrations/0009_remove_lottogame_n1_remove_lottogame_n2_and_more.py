# Generated by Django 4.2.7 on 2023-12-03 22:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("lotto", "0008_lottogame_n1_lottogame_n2_lottogame_n3_lottogame_n4_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lottogame",
            name="n1",
        ),
        migrations.RemoveField(
            model_name="lottogame",
            name="n2",
        ),
        migrations.RemoveField(
            model_name="lottogame",
            name="n3",
        ),
        migrations.RemoveField(
            model_name="lottogame",
            name="n4",
        ),
        migrations.RemoveField(
            model_name="lottogame",
            name="n5",
        ),
        migrations.RemoveField(
            model_name="lottogame",
            name="n6",
        ),
        migrations.RemoveField(
            model_name="usernumbers",
            name="n1",
        ),
        migrations.RemoveField(
            model_name="usernumbers",
            name="n2",
        ),
        migrations.RemoveField(
            model_name="usernumbers",
            name="n3",
        ),
        migrations.RemoveField(
            model_name="usernumbers",
            name="n4",
        ),
        migrations.RemoveField(
            model_name="usernumbers",
            name="n5",
        ),
        migrations.RemoveField(
            model_name="usernumbers",
            name="n6",
        ),
    ]
