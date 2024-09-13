from django.db import models

# Models
class IDXTotalMarketCap(models.Model):
    date = models.DateField()
    idx_total_market_cap = models.BigIntegerField(blank=True, null=True)
    
    class Meta:
        db_table = "idx_total_market_cap"

class IndexDaily(models.Model):
    date = models.DateField()
    index_code = models.CharField(max_length=20)
    price = models.DecimalField(decimal_places=2, max_digits=12)
    
    class Meta:
        db_table = "index_daily"

class TickerList(models.Model):
    symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255)

    class Meta:
        db_table = "idx_tickers"

class TickerDaily(models.Model):
    date = models.DateField()
    symbol = models.CharField(max_length=10)
    open = models.IntegerField(blank=True, null=True)
    high = models.IntegerField(blank=True, null=True)
    low = models.IntegerField(blank=True, null=True)
    close = models.IntegerField(blank=True, null=True)
    volume = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "ticker_daily"

class BalanceSh(models.Model):
    year = models.CharField(max_length=6)
    symbol = models.CharField(max_length=10)
    assets = models.BigIntegerField(blank=True, null=True)
    liabilities = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "balance_sh"

class CashFlow(models.Model):
    year = models.CharField(max_length=10)
    symbol = models.CharField(max_length=10)
    operating_cf = models.BigIntegerField(blank=True, null=True)
    investing_cf = models.BigIntegerField(blank=True, null=True)
    financing_cf = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "cash_flow"

class IncomeStatement(models.Model):
    year = models.CharField(max_length=10)
    symbol = models.CharField(max_length=10)
    total_revenue = models.BigIntegerField(blank=True, null=True)
    net_income = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "income_stmt"

class TickerOverview(models.Model):
    symbol = models.CharField(primary_key=True, max_length=10)
    company_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=255)
    sub_sector = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    sub_industry = models.CharField(max_length=255)
    listing_date = models.CharField(max_length=20)
    website = models.CharField(max_length=255)

    class Meta:
        db_table = "ticker_overview"