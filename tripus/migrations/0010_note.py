# Generated by Django 3.0.8 on 2020-08-21 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tripus', '0009_trip_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tripus.Trip')),
            ],
        ),
    ]
