# Generated by Django 4.1.7 on 2023-05-15 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("boards", "0004_run_has_vid_run_is_obsolete_runner_points_overall_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="runner",
            name="points_m1",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="runner",
            name="points_m2",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="runner",
            name="points_m3",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="runner",
            name="points_m4",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="runner",
            name="points_m5",
            field=models.IntegerField(default=0),
        ),
    ]
