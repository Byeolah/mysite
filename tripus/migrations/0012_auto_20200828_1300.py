# Generated by Django 3.0.8 on 2020-08-28 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tripus', '0011_auto_20200828_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='file',
            field=models.FileField(blank=True, upload_to='tickets/'),
        ),
    ]
