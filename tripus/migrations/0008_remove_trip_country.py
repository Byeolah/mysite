# Generated by Django 3.0.8 on 2020-08-20 10:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tripus', '0007_visit_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip',
            name='country',
        ),
    ]
