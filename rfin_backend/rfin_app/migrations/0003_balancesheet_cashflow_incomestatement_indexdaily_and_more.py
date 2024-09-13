# Generated by Django 4.2.16 on 2024-09-11 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rfin_app', '0002_alter_idxmarketcap_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='BalanceSheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.SmallIntegerField()),
                ('symbol', models.CharField(max_length=10)),
                ('total_assets', models.BigIntegerField(blank=True, null=True)),
                ('total_debt', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'balance_sheet',
            },
        ),
        migrations.CreateModel(
            name='CashFlow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.SmallIntegerField()),
                ('symbol', models.CharField(max_length=10)),
                ('operating_cf', models.BigIntegerField(blank=True, null=True)),
                ('investing_cf', models.BigIntegerField(blank=True, null=True)),
                ('financing_cf', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cash_flow',
            },
        ),
        migrations.CreateModel(
            name='IncomeStatement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.SmallIntegerField()),
                ('symbol', models.CharField(max_length=10)),
                ('total_revenue', models.BigIntegerField(blank=True, null=True)),
                ('net_income', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'income_stmt',
            },
        ),
        migrations.CreateModel(
            name='IndexDaily',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('index_code', models.CharField(max_length=20)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
            options={
                'db_table': 'index_daily',
            },
        ),
        migrations.CreateModel(
            name='TickerDaily',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('symbol', models.CharField(max_length=10)),
                ('open', models.IntegerField(blank=True, null=True)),
                ('high', models.IntegerField(blank=True, null=True)),
                ('low', models.IntegerField(blank=True, null=True)),
                ('close', models.IntegerField(blank=True, null=True)),
                ('volume', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ticker_daily',
            },
        ),
    ]
