# Generated by Django 5.0.2 on 2024-04-12 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='newssource',
            name='is_startup_news',
            field=models.BooleanField(default=True),
        ),
    ]
