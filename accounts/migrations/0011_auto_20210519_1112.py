# Generated by Django 3.1.7 on 2021-05-19 05:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20210519_0221'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PhoneOTP',
        ),
        migrations.AlterField(
            model_name='account',
            name='phone_number',
            field=models.CharField(max_length=17, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Phone number must be entered in the format +919999999999. Up to 10 digits allowed.', regex='^\\+?1?\\d{9,10}$')], verbose_name='Phone'),
        ),
    ]