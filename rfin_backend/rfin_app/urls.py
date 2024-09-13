from django.urls import path, re_path
from .views import *

urlpatterns = [
    re_path('signup', signup),
    re_path('login', login),
    re_path('test_token', test_token),
    path("idx-total-market-cap", IDXTotalMarketCapView.as_view(), name="idx-total-market-cap"),
    path("index-daily", IndexDailyView.as_view(), name="index-daily"),
    path("ticker-list", TickerListView.as_view(), name="ticker-list"),
    path("ticker-daily", TickerDailyView.as_view(), name="ticker-daily"),
    path("balance-sheet", BalanceSheetView.as_view(), name="balance-sheet"),
    path("cash-flow", CashFlowView.as_view(), name="cash-flow"),
    path("income-statement", IncomeStatementView.as_view(), name="income-statement"),
    path("ticker-overview", TickerOverviewView.as_view(), name="ticker-overview"),
]
