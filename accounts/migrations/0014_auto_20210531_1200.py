# Generated by Django 3.1.7 on 2021-05-31 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_userprofile_referral_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='referral_count',
        ),
        migrations.AddField(
            model_name='account',
            name='referral_count',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
    ]
