# Generated by Django 3.1.7 on 2021-05-03 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
