# Generated by Django 3.0.8 on 2020-08-12 18:02

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tripus', '0002_auto_20200806_1019'),
    ]

    operations = [
        migrations.CreateModel(
            name='Spending',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('currency_code', models.CharField(max_length=3)),
                ('date', models.DateField(default=datetime.date.today)),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tripus.Trip')),
            ],
        ),
    ]