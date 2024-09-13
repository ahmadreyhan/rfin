from django.contrib import admin
from .models import *

# Registering models
admin.site.register(IDXTotalMarketCap)
admin.site.register(IndexDaily)
admin.site.register(TickerList)
admin.site.register(TickerDaily)
admin.site.register(BalanceSh)
admin.site.register(CashFlow)
admin.site.register(IncomeStatement)
admin.site.register(TickerOverview)