# Generated by Django 4.2.16 on 2024-09-12 02:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rfin_app', '0019_balancesh'),
    ]

    operations = [
        migrations.RenameField(
            model_name='balancesh',
            old_name='total_assets',
            new_name='assets',
        ),
        migrations.RenameField(
            model_name='balancesh',
            old_name='total_debt',
            new_name='liabilities',
        ),
    ]
