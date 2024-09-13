from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User 
        fields = ['email', 'username', 'password', 'first_name', 'last_name']

class IDXTotalMarketCapSerializer(serializers.ModelSerializer):
    class Meta:
        model = IDXTotalMarketCap
        fields = '__all__'

class IndexDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = IndexDaily
        fields = '__all__'

class TickerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TickerList
        fields = '__all__'

class TickerDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = TickerDaily
        fields = '__all__'

class BalanceSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceSh
        fields = '__all__'

class CashFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashFlow
        fields = '__all__'

class IncomeStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeStatement
        fields = '__all__'

class TickerOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TickerOverview
        fields = '__all__'