# Generated by Django 4.1.7 on 2023-03-29 14:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Mission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("CE", "City Escape"),
                            ("WC", "Wild Canyon"),
                            ("PL", "Prison Lane"),
                            ("MHa", "Metal Harbor"),
                            ("GF", "Green Forest"),
                            ("PH", "Pumpkin Hill"),
                            ("MSt", "Mission Street"),
                            ("AM", "Aquatic Mine"),
                            ("101", "Route 101"),
                            ("HB", "Hidden Base"),
                            ("PC", "Pyramid Cave"),
                            ("DC", "Death Chamber"),
                            ("EE", "Eternal Engine"),
                            ("MHe", "Meteor Herd"),
                            ("CG", "Crazy Gadget"),
                            ("FR", "Final Rush"),
                            ("IG", "Iron Gate"),
                            ("DL", "Dry Lagoon"),
                            ("SO", "Sand Ocean"),
                            ("RH", "Radical Highway"),
                            ("EQ", "Egg Quarters"),
                            ("LC", "Lost Colony"),
                            ("WB", "Weapons Bed"),
                            ("SH", "Security Hall"),
                            ("WJ", "White Jungle"),
                            ("280", "Route 280"),
                            ("SR", "Sky Rail"),
                            ("MSp", "Mad Space"),
                            ("CW", "Cosmic Wall"),
                            ("FC", "Final Chase"),
                            ("CC", "Cannons Core"),
                            ("GH", "Green Hill"),
                        ],
                        default="GH",
                        max_length=3,
                    ),
                ),
                ("mnum", models.SmallIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="Runner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tsc_username", models.TextField()),
                ("tsc_as_primary", models.BooleanField(default=False)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Run",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("time_s", models.DecimalField(decimal_places=2, max_digits=7)),
                (
                    "source",
                    models.CharField(
                        choices=[("TSC", "SONICCENTER"), ("SRC", "SPEEDRUN.COM")],
                        default="TSC",
                        max_length=3,
                    ),
                ),
                ("date_performed", models.DateField()),
                (
                    "mission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="boards.mission"
                    ),
                ),
                (
                    "runner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="boards.runner"
                    ),
                ),
            ],
        ),
    ]
