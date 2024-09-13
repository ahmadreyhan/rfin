from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .models import *
from .serializers import *
from django.core.cache import cache
from rest_framework.response import Response
from django.db.models import Q

from datetime import date

# Views
@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_200_OK)

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response(f"passed for {request.user.email}")

class IDXTotalMarketCapView(ListAPIView):
    queryset = IDXTotalMarketCap.objects.all()
    serializer_class = IDXTotalMarketCapSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if start_date:
            queryset = queryset.filter(date__range=[start_date, date.today()])
        elif end_date:
            queryset = queryset.filter(date__range=["2024-06-21", date.today()])
        elif start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        return queryset
    
    def list(self, request):
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if start_date:
            cache_key = f"idx-market-cap: {start_date}"
        elif end_date:
            cache_key = f"idx-market-cap: {end_date}"
        elif start_date and end_date:
            cache_key = f"idx-market-cap: {start_date}-{end_date}"
        result = cache.get(cache_key)
        if not result:
            print("Hitting DB")
            result = self.get_queryset()     
            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        return Response(result.data)
    
class IndexDailyView(ListAPIView):
    queryset = IndexDaily.objects.all()
    serializer_class = IndexDailySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        index_code = self.request.query_params.get("index_code", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if index_code:
            index_code = index_code.upper()
            queryset = queryset.filter(index_code__contains=index_code)
        elif start_date:
            queryset = queryset.filter(date__range=[start_date, date.today()])
        elif end_date:
            queryset = queryset.filter(date__range=["2024-06-21", end_date])
        elif start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        else:
            queryset
        return queryset

    def list(self, request):
        index_code = self.request.query_params.get("index_code", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if index_code:
            cache_key = f"index-daily: {index_code}"
        elif start_date:
            cache_key = f"index-daily: {index_code}-{start_date}"
        elif end_date:
            cache_key = f"index-daily: {index_code}-{end_date}"
        elif start_date and end_date:
            cache_key = f"index-daily: {index_code}-{start_date}-{end_date}"
        else:
            cache_key = "all"
        result = cache.get(cache_key)
        if not result:
            print("Hitting DB")
            result = self.get_queryset()     
            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        return Response(result.data) 
    
class TickerListView(ListAPIView):
    queryset = TickerList.objects.all()
    serializer_class = TickerListSerializer

    def get_queryset(self):
        return super().get_queryset()

class TickerDailyView(ListAPIView):
    queryset = TickerDaily.objects.all()
    serializer_class = TickerDailySerializer

    def list(self, request):
        cache_key = "ticker-list"
        result = cache.get(cache_key)
        if not result:
            print("Hitting DB")
            result = self.get_queryset()     
            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        return Response(result.data)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get("symbol", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if symbol:
            symbol = symbol.upper()
            if not symbol.endswith(".JK"):
                symbol = f"{symbol}.JK"
            queryset = queryset.filter(symbol__contains=symbol)
        elif start_date:
            queryset = queryset.filter(Q(symbol__contains=symbol) & Q(date__range=[start_date, date.today()]))
        elif end_date:
            queryset = queryset.filter(Q(symbol__contains=symbol) & Q(date__range=["2024-06-21", end_date]))
        elif start_date and end_date:
            queryset = queryset.filter(Q(symbol__contains=symbol) & Q(date__range=[start_date, end_date]))
        return queryset

    def list(self, request):
        symbol = self.request.query_params.get("symbol", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if symbol:
            cache_key = f"ticker-daily: {symbol}"
        elif start_date:
            cache_key = f"ticker-daily: {symbol}-{start_date}"
        elif end_date:
            cache_key = f"ticker-daily: {symbol}-{end_date}"
        elif start_date and end_date:
            cache_key = f"ticker-daily: {symbol}-{start_date}-{end_date}"
        result = cache.get(cache_key)
        if not result:
            print("Hitting DB")
            result = self.get_queryset()     
            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        return Response(result.data)
    
class BalanceSheetView(ListAPIView):
    queryset = BalanceSh.objects.all()
    serializer_class = BalanceSheetSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get("symbol", None)
        year = self.request.query_params.get("year", None)
        if symbol and year:
            symbol = symbol.upper()
            if not symbol.endswith(".JK"):
                symbol = f"{symbol}.JK"
            queryset = queryset.filter(
                Q(symbol__contains=symbol) & Q(year__contains=year))
        elif symbol:
            symbol = symbol.upper()
            if not symbol.endswith(".JK"):
                symbol = f"{symbol}.JK"
            queryset = queryset.filter(symbol__contains=symbol)
        elif year:
            queryset = queryset.filter(year__contains=year)
        return queryset
    
    def list(self, request):
        symbol = self.request.query_params.get("symbol", None)
        year = self.request.query_params.get("year", None)
        if symbol:
            cache_key = f"balance-sheet: {symbol}"
        elif year:
            cache_key = f"balance-sheet: {year}"
        elif symbol and year:
            cache_key = f"balance-sheet: {symbol}-{year}"
        result = cache.get(cache_key)
        if not result:
            print("Hitting DB")
            result = self.get_queryset()     
            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        return Response(result.data)
    
class CashFlowView(ListAPIView):
    queryset = CashFlow.objects.all()
    serializer_class = CashFlowSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get("symbol", None)
        year = self.request.query_params.get("year", None)
        if symbol and year:
            symbol = symbol.upper()
            if not symbol.endswith(".JK"):
                symbol = f"{symbol}.JK"
            queryset = queryset.filter(
                Q(symbol__contains=symbol) & Q(year__contains=year))
        elif symbol:
            symbol = symbol.upper()
            if not symbol.endswith(".JK"):
                symbol = f"{symbol}.JK"
            queryset = queryset.filter(symbol__contains=symbol)
        elif year:
            queryset = queryset.filter(year__contains=year)
        return queryset
    
    def list(self, request):
        symbol = self.request.query_params.get("symbol", None)
        year = self.request.query_params.get("year", None)
        if symbol:
            cache_key = f"cash-flow: {symbol}"
        elif year:
            cache_key = f"cash-flow: {year}"
        elif symbol and year:
            cache_key = f"cash-flow: {symbol}-{year}"
        result = cache.get(cache_key)
        if not result:
            print("Hitting DB")
            result = self.get_queryset()     
            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        return Response(result.data)
    
class IncomeStatementView(ListAPIView):
    queryset = IncomeStatement.objects.all()
    serializer_class = IncomeStatementSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get("symbol", None)
        year = self.request.query_params.get("year", None)
        if symbol and year:
            symbol = symbol.upper()
            if not symbol.endswith(".JK"):
                symbol = f"{symbol}.JK"
            queryset = queryset.filter(
                Q(symbol__contains=symbol) & Q(year__contains=year))
        elif symbol:
            symbol = symbol.upper()
            if not symbol.endswith(".JK"):
                symbol = f"{symbol}.JK"
            queryset = queryset.filter(symbol__contains=symbol)
        elif year:
            queryset = queryset.filter(year__contains=year)
        return queryset
    
    def list(self, request):
        symbol = self.request.query_params.get("symbol", None)
        year = self.request.query_params.get("year", None)
        if symbol:
            cache_key = f"income-stmt: {symbol}"
        elif year:
            cache_key = f"income-stmt: {year}"
        elif symbol and year:
            cache_key = f"income-stmt: {symbol}-{year}"
        result = cache.get(cache_key)
        if not result:
            print("Hitting DB")
            result = self.get_queryset()     
            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        return Response(result.data)
    
class TickerOverviewView(ListAPIView):
    queryset = TickerOverview.objects.all()
    serializer_class = TickerOverviewSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get("symbol", None)
        if symbol:
            symbol = symbol.upper()
            if not symbol.endswith(".JK"):
                symbol = f"{symbol}.JK"
            queryset = queryset.filter(symbol__contains=symbol)
        return queryset
    
    def list(self, request):
        symbol = self.request.query_params.get("symbol", None)
        if symbol:
            cache_key = f"ticker-overview: {symbol}"
        result = cache.get(cache_key)
        if not result:
            print("Hitting DB")
            result = self.get_queryset()     
            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        return Response(result.data)