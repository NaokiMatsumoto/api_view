# Generated by Django 5.0.2 on 2025-03-13 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweetprompt',
            name='target_url',
            field=models.TextField(blank=True, verbose_name='遷移先URL'),
        ),
    ]
