# Generated by Django 4.2.7 on 2024-02-11 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DbApplication', '0006_topdestination'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topdestination',
            name='price_amount',
            field=models.CharField(max_length=20),
        ),
    ]
