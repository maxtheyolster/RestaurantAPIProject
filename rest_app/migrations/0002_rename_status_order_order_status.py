# Generated by Django 4.2.5 on 2023-09-27 00:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='status',
            new_name='order_status',
        ),
    ]
