# Generated by Django 3.1.7 on 2021-05-20 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20210518_2353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Shipped', 'Shipped'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Accepted', max_length=10),
        ),
    ]
