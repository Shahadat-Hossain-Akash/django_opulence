# Generated by Django 5.0.1 on 2024-02-12 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_transaction_options_transaction_balance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='balance',
        ),
    ]
