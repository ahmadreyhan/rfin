# Generated by Django 4.2.16 on 2024-09-11 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rfin_app', '0006_alter_balancesheet_year_alter_cashflow_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balancesheet',
            name='year',
            field=models.SmallIntegerField(),
        ),
    ]
