# Generated by Django 3.1.7 on 2021-05-31 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_auto_20210531_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='referral_count',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
