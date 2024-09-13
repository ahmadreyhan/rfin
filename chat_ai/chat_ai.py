# Import package(s)
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
from pytanggalmerah import TanggalMerah
from typing import Union, Literal, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 
from streamlit.delta_generator import DeltaGenerator

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
SECTORS_API_KEY = os.getenv('SECTORS_API_KEY')

def _retrieve_from_endpoint(url: str):
    """
    Retrieve the financial data from the Sectors API according to the url.

    Arg(s): 
        - url (str): The url to Sectors API hit
    Return(s):
        a Python string that contains requested financial data
    """
    headers = {"Authorization": SECTORS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    
def is_saturday_sunday(date: datetime) -> bool:
    """
    Check whether the date is saturday or sunday
    
    Arg(s):
        - date (datetime) : Passed date in datetime format
    Return(s):
        a Python boolean True if the date is either saturday or sunday
    """
    day = date.strftime("%A")
    if day in ["Saturday", "Sunday"]:
        return True
    else:
        return False
    
def is_weekend_holiday(date: datetime) -> bool:
    """
    Check a date either weekend or holiday

    Arg(s):
        - date (datetime) : Passed date in datetime format
    Return(s):
        a Python boolean True if the date is either weekend or holiday
    """
    t = TanggalMerah(cache_path=None, cache_time=600)
    t.set_date(date.year, date.month, date.day)
    if is_saturday_sunday(date) is True or t.is_holiday() is True:
        return True 
    else:
        return False
    
def get_last_n_dates(last_n_dates: int = 5) -> dict:
    """
    Get last n dates for determine start and end date to date-context range tools, the idea is to exclude the weekends and holidays in date range.
    The result could be pass to another tools that need start and end date range parameter if the user prompt not explicitly provided.

    Arg(s):
        - last_n_dates (int): Number for the requested last n days data
    Return(s):
        a Python dictionary that contains proper start and end date range
    """
    end_date = datetime.today() - timedelta(days=1)
    list_of_dates = []
    while last_n_dates > 0:
        date_to_check = end_date
        if is_weekend_holiday(date_to_check) is False:
            list_of_dates.append(date_to_check)
            last_n_dates -= 1
        end_date = end_date - timedelta(days=1)
    return {'start_date': list_of_dates[-1].strftime('%Y-%m-%d'), 
            'end_date': list_of_dates[0].strftime('%Y-%m-%d')}

def helper_list_subsectors() -> list:
    """
    Retrieve the list of subsectors available in IDX

    Return(s):
        a Python list of dictionary contains list of subsectors and the corresponding industries for each subsector in IDX.
    """
    url = "https://api.sectors.app/v1/subsectors/"
    return _retrieve_from_endpoint(url)

def helper_list_subindustries() -> list:
    """
    Retrieve the list of subindustries available in IDX

    Return(s):
        a Python list of dictionary contains list of subindustries and the corresponding industries for each subindustry in IDX.
    """
    url = "https://api.sectors.app/v1/subindustries/"
    return _retrieve_from_endpoint(url)

def simple_line_chart(df: pd.DataFrame, x_y_axis: list, x_y_label: list, chart_title: str) -> go.Figure:
    """
    A helper function to get a simple line chart figure using Plotly Express.

    Arg(s):
        - df (DataFrame): a dataframe contains 2 columns data for line chart
        - x_y_axis (list): a list for x and y axis name
        - x_y_label (list): a list for x and y axis label display in chart
        - chart_title (str): desired chart title

    Return(s):
        a simple line chart figure
    """
    return px.line(df, x=x_y_axis[0], y=x_y_axis[1], template="plotly", title=chart_title, labels={x_y_axis[0]: x_y_label[0], x_y_axis[1]:x_y_label[1]}, line_shape="spline")

def simple_bar_chart(df: pd.DataFrame, x_y_axis: list, x_y_label: list, chart_title: str, custom_text: Optional[Union[str, list]]=None) -> go.Figure:
    """
    A helper function to get a simple bar chart figure using Plotly Express.

    Arg(s):
        - df (DataFrame): a dataframe contains 2 columns data for line chart
        - x_y_axis (list): a list for x and y axis name
        - x_y_label (list): a list for x and y axis label display in chart
        - chart_title (str): desired chart title
        - custom_text (str | list): Optional parameter for custom text label

    Return(s):
        a simple bar chart figure
    """
    if custom_text:
        return px.bar(df, x=x_y_axis[0], y=x_y_axis[1], text=custom_text, template="plotly", title=chart_title, labels={x_y_axis[0]: x_y_label[0], x_y_axis[1]:x_y_label[1]})
    else:
        return px.bar(df, x=x_y_axis[0], y=x_y_axis[1], text_auto='.2s', template="plotly", title=chart_title, labels={x_y_axis[0]: x_y_label[0], x_y_axis[1]:x_y_label[1]})

@tool
def list_subsectors() -> pd.DataFrame:
    """
    Retrieve the list of subsectors available in IDX

    Return(s):
        a Pandas DataFrame contains list of subsectors and the corresponding industries for each subsector in IDX.
    """
    url = "https://api.sectors.app/v1/subsectors/"
    returned_data = _retrieve_from_endpoint(url)
    data = {"sector": [d["sector"].replace('-',' ') for d in returned_data],
            "sub_sector" : [d["subsector"].replace('-',' ') for d in returned_data]}
    return pd.DataFrame(data).sort_values("sector", ascending=True)

@tool
def list_industries() -> pd.DataFrame:
    """
    Retrieve the list of industries available in IDX

    Return(s):
        a Pandas DataFrame contains list of industries and the corresponding subsectors for each industry in IDX.
    """
    url = "https://api.sectors.app/v1/industries/"
    returned_data = _retrieve_from_endpoint(url)
    data = {"sub_sector": [d["subsector"].replace('-',' ') for d in returned_data],
            "industry" : [d["industry"].replace('-',' ') for d in returned_data]}
    return pd.DataFrame(data).sort_values("sub_sector", ascending=True)

@tool
def list_subindustries() -> pd.DataFrame:
    """
    Retrieve the list of subindustries available in IDX

    Return(s):
        a Pandas DataFrame contains list of subindustries and the corresponding industries for each subindustry in IDX.
    """
    url = "https://api.sectors.app/v1/subindustries/"
    returned_data = _retrieve_from_endpoint(url)
    data = {"industry": [d["industry"].replace('-',' ') for d in returned_data],
            "sub_industry" : [d["sub_industry"].replace('-',' ') for d in returned_data]}
    return pd.DataFrame(data).sort_values("industry", ascending=True)

@tool
def list_companies_by_subsectors(subsector: str) -> pd.DataFrame:
    """
    Retrieve the list of companies by subsectors available in IDX

    Args(s):
        - subsector (str): Choosen sub-sector in IDX
    Return(s):
        a Python list of dictionary contains list of companies (ticker symbol and company name) by subsectors in IDX.
    """
    subsector = subsector.title()
    valid_subsectors = [d["subsector"].replace('-',' ').title() for d in helper_list_subsectors()]
    assert subsector in valid_subsectors, f"Invalid sub-sector: {subsector}\n The sub-sector must be one of {valid_subsectors}\n Please specify a sub-sector from documentation"
    url = f"https://api.sectors.app/v1/companies/?sub_sector={subsector.replace(' ', '-').lower()}"
    returned_data = _retrieve_from_endpoint(url)
    data = {"symbol": [d["symbol"] for d in returned_data],
            "company_name" : [d["company_name"] for d in returned_data]}
    df = pd.DataFrame(data).sort_values("symbol", ascending=True)
    df.index = np.arange(1, len(df)+1)
    return df

@tool
def list_companies_by_subindustries(subindustry: str) -> pd.DataFrame:
    """
    Retrieve the list of companies by subindustries available in IDX
    
    Args(s):
        - subindustry (str): Choosen sub-industry in IDX 
    Return(s):
        a Python list of dictionary contains list of companies (ticker symbol and company name) by subsindustries in IDX.
    """
    subindustry = subindustry.title()
    valid_subindustries = [d["sub_industry"].replace('-',' ').title() for d in helper_list_subindustries()]
    assert subindustry in valid_subindustries, f"Invalid sub-industry: {subindustry}\n The sub-industry must be one of {valid_subindustries}\n Please specify a sub-industry from documentation"
    url = f"https://api.sectors.app/v1/companies/?sub_industry={subindustry.replace(' ', '-').lower()}"
    returned_data = _retrieve_from_endpoint(url)
    data = {"symbol": [d["symbol"] for d in returned_data],
            "company_name" : [d["company_name"] for d in returned_data]}
    df = pd.DataFrame(data).sort_values("symbol", ascending=True)
    df.index = np.arange(1, len(df)+1)
    return df

@tool
def list_companies_by_index(index: str) -> pd.DataFrame:
    """
    Retrieve the list of companies by index available in IDX

    Arg(s):
        - index (str): One of following index: FTSE, IDX30, IDXBUMN20, IDXESGL, IDXG30, IDXHIDIV20, IDXQ30, IDXV30, JII70, KOMPAS100, LQ45, SMINFRA18, SRIKEHATI
    Return(s):
        a Python list of dictionary contains list of companies (ticker symbol and company name) by index in IDX.
    """
    valid_index = ["FTSE", "IDX30", "IDXBUMN20", "IDXESGL", "IDXG30", "IDXHIDIV20", "IDXQ30", "IDXV30", "JII70", "KOMPAS100", "LQ45", "SMINFRA18", "SRIKEHATI"]
    assert index in valid_index, f"Invalid index: {index}\n The index must be one of {valid_index}\n Please specify an index from documentation"
    url = f"https://api.sectors.app/v1/index/{index.lower()}/"
    returned_data = _retrieve_from_endpoint(url)
    data = {"symbol": [d["symbol"] for d in returned_data],
            "company_name" : [d["company_name"] for d in returned_data]}
    df = pd.DataFrame(data).sort_values("symbol", ascending=True)
    df.index = np.arange(1, len(df)+1)
    return df

@tool
def companies_performance_since_ipo(ticker: str) -> dict:
    """
    Retrieve the stock price performance since Initial Public Offering (IPO), i.e price change since IPO, including 7 days, 30 days, 90 days, and 365 days after IPO.

    Arg(s):
        - ticker (str): 4-digits ticker stock of a company in IDX, e.g. BBRI
    Return(s):
        - a Python dictionary that contains stock price changes of the company since Initial Public Offering (IPO)
    """
    url = f"https://api.sectors.app/v1/listing-performance/{ticker}/"
    return _retrieve_from_endpoint(url)

@tool
def get_company_info(ticker: str,
                     section: str = "Overview") -> list:
    """
    Retrieve financial data for a specific stock and section from the Sectors API.

    Arg(s): 
        - ticker (str): 4-digits ticker stock of a company in IDX, e.g. BBRI
        - section (str) : One of following section (default to Overview): Dividend, Financials, Future, Management, Overview, Ownership, Peers, Valuation
                      a. Dividend contains historical dividens, annual yield, average yield, dividend payout ratio, dividend cash payout ratio,  and last ex dividend date;
                      b. Financials contains historical financials including tax, revenue, earnings, cash only, total debt, fixed asset, gross profit, total assets, total equity, operating PNL, total liabilities, current liabilities, earnings before tax, cash and equivalents, total cash and due from banks, then interest coverafe ratio, cash flow debt ratio, Debt-Equity Ratio (DER), Debt-Asset Ratio (DAR), Return on Asset (ROA), Return on Equity (ROE), Year-on-Year quarter earnings growth, Year-on-Year quarter earnings growth, and net profit margin;
                      c. Future contains some future insights for the stock including company value and growth forecasts, technical rating breakdown, up to analyst rating breakdown;
                      d. Management contains key executives including President Director, Vice President Director, and Directors, then also the executives shareholdings;
                      e. Overview contains listing board, industry, sub industry, sector, sub sector, market capitalization and its rank in IDX, address, number of employee, listing date, website, phone, email, last close price, latest close date, and latest daily close price change;
                      f. Ownership contains major shareholders list then top transactions including top buyers and sellers then also monthly net transactions;
                      g. Peers contains peers in same sector, sub sector, industry, and sub industry, including peers's financial information;
                      h. Valuation contains some valuations of the stock and its historical valuations including Price to Book (PB), Price to Earnings (PE), Price to Sales (PS), and their yearly average.
    Return(s):
         a Python list of dictionary contains financial data of the requested ticker and section
    """
    valid_sections = ["Overview", "Valuation", "Future", "Peers", 
                      "Financials", "Dividend", "Management", "Ownership"]
    assert section in valid_sections, f"Invalid section: {section}\n The section must be one of {valid_sections}\n Please specify a section from documentation"
    url = f"https://api.sectors.app/v1/company/report/{ticker}/?sections={section.lower()}"
    return _retrieve_from_endpoint(url)

@tool
def get_top_companies_by_trx_volume(start_date: str, end_date: str, top_n: int = 5, subsector: str = None) -> Union[str, DeltaGenerator, list]:
    """
    Retrieve the top-n companies that the highest transaction volume or most traded within the date range (start from start_date parameter up to end_date parameter inclusive), default is top-5
    Subsector parameter could be used if there is specifying subsector

    Arg(s): 
        - start_date (str): The start date of requested date range
        - end_date (str) : The end date of requested date range
        - top_n (int) : The requested number (n) of highest transaction volume
        - subsector (str): Specific sub-sector, set to None default, if it's not defined then retrieve all sub-sectors combined
    Return(s):
        - Stringed Pandas DataFrame contains top-n companies based on transaction volume within date range
        - Streamlit containter for plotly chart figure
        - List contains the skipped date because of either weekend or holidays
    """
    holiday_list = []
    while is_weekend_holiday(datetime.strptime(end_date, "%Y-%m-%d")) is True:
        holiday_list.append(f"{end_date} is either weekend or holiday")
        end_date = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    if subsector is None:
        url = f"https://api.sectors.app/v1/most-traded/?start={start_date}&end={end_date}&n_stock={top_n}"
    else:
        subsector = subsector.title()
        valid_subsector = [d["subsector"].replace('-',' ').title() for d in helper_list_subsectors()]
        assert subsector in valid_subsector, f"Invalid sub-sector: {subsector}\n The sub-sector must be one of {valid_subsector}\n Please specify a sub-sector from documentation"
        url = f"https://api.sectors.app/v1/most-traded/?start={start_date}&end={end_date}&n_stock={top_n}&sub_sector={subsector.replace(' ', '-').lower()}"
    returned_data = _retrieve_from_endpoint(url)
    data = {'Symbol': [index["symbol"] for date in returned_data for index in returned_data[date]],
            'Company Name' : [index["company_name"] for date in returned_data for index in returned_data[date]],
            'Volume (Shares)': [index["volume"] for date in returned_data for index in returned_data[date]],
            'Price (Rp/Share)': [index["price"] for date in returned_data for index in returned_data[date]]}
    df = pd.DataFrame(data).groupby(["Symbol", "Company Name"]).agg({"Volume (Shares)": "sum", "Price (Rp/Share)":"mean"}).sort_values('Volume (Shares)', ascending=False).reset_index().rename(columns={"Volume (Shares)": "Total Volume (Shares)", "Price (Rp/Share)": "Average Price (Rp/Share)"}).sort_values('Total Volume (Shares)', ascending=False).head(top_n)
    fig = simple_bar_chart(df=df, x_y_axis=["Symbol", "Total Volume (Shares)"], x_y_label=["Ticker Symbol", "Total Volume (Shares)"], chart_title=f"Top Companies by Transaction Volume within {start_date} - {end_date}", custom_text=['{:.2}B'.format(x / 1000000000) for x in df["Total Volume (Shares)"]])
    return df.to_string(), st.plotly_chart(fig), holiday_list

@tool
def get_top_companies_by_trx_volume_last_n_dates(top_n: int = 5, last_n_dates: int = 5, subsector: str = None) -> Union[str, DeltaGenerator]:
    """
    Retrieve the top-n companies that the highest transaction volume if the start and end dates not explicitly provided, i.e. requested the top companies in last n day(s)
    Subsector argument could be used if there is defined specific sub-sector.

    Arg(s): 
        - top_n (int): The requested number (n) of highest transaction volume
        - last_n_dates (int): Number for the requested last n days data
        - subsector (str): Specific sub-sector, default set to None if it's not specified
    Return(s):
        - Stringed Pandas DataFrame contains top-n companies based on transaction volume in last n date(s)
        - Streamlit container for plotly chart figure
    """
    if subsector is None:
        url = f"https://api.sectors.app/v1/most-traded/?start={get_last_n_dates(last_n_dates)['start_date']}&end={get_last_n_dates(last_n_dates)['end_date']}&n_stock={top_n}"
    else:
        subsector = subsector.title()
        valid_subsector = [d["subsector"].replace('-',' ').title() for d in helper_list_subsectors()]
        assert subsector in valid_subsector, f"Invalid sub-sector: {subsector}\n The sub-sector must be one of {valid_subsector}\n Please specify a sub-sector from documentation"
        url = f"https://api.sectors.app/v1/most-traded/?start={get_last_n_dates(last_n_dates)['start_date']}&end={get_last_n_dates(last_n_dates)['end_date']}&n_stock={top_n}&sub_sector={subsector.replace(' ', '-').lower()}"
    returned_data = _retrieve_from_endpoint(url)
    data = {'Symbol': [index["symbol"] for date in returned_data for index in returned_data[date]],
            'Company Name' : [index["company_name"] for date in returned_data for index in returned_data[date]],
            'Volume (Shares)': [index["volume"]  for date in returned_data for index in returned_data[date]],
            'Price (Rp/Share)': [index["price"] for date in returned_data for index in returned_data[date]]}
    df = pd.DataFrame(data).groupby(["Symbol", "Company Name"]).agg({"Volume (Shares)": "sum", "Price (Rp/Share)":"mean"}).sort_values('Volume (Shares)', ascending=False).reset_index().rename(columns={"Volume (Shares)": "Total Volume (Shares)", "Price (Rp/Share)": "Average Price (Rp/Share)"}).head(top_n)
    fig = simple_bar_chart(df=df, x_y_axis=["Symbol", "Total Volume (Shares)"], x_y_label=["Ticker Symbol", "Total Volume (Shares)"], chart_title=f"Top Companies by Transaction Volume in  last {last_n_dates} day(s): within {get_last_n_dates(last_n_dates)['start_date']} - {get_last_n_dates(last_n_dates)['end_date']}", custom_text=['{:.2}B'.format(x / 1000000000) for x in df["Total Volume (Shares)"]])
    return df.to_string(), st.plotly_chart(fig)

@tool
def get_top_companies_by_section(subsector: str, top_n: int, section: str = "market_cap", year: int = datetime.today().year) -> Union[str, DeltaGenerator]:
    """
    Retrieve the top-n companies based on some sections, i.e. dividend yield, earnings, market capitalization, revenue, and total dividend

    Arg(s):
        - subsector (str): Choosen sub-sector in IDX
        - top_n (int): The requested number (n) of top in a section
        - section (str): One of following section (default to Market Cap): Dividend Yield, Earnings, Market Cap, Revenue, Total Dividend
        - year (int): Desired year to display, default to the current year
    Return(s):
        - Stringed Pandas DataFrame contains top-n companies based on the requested section
        - Streamlit containter for plotly chart figure
    """
    subsector = subsector.title()
    valid_subsectors = [d["subsector"].replace('-',' ').title() for d in helper_list_subsectors()]
    assert subsector in valid_subsectors, f"Invalid sub-sector: {subsector}\n The sub-sector must be one of {valid_subsectors}\n Please specify a sub-sector from documentation"

    section = section.title().replace('_', ' ')
    valid_sections = ["Dividend Yield", "Earnings", "Market Cap", "Revenue", "Total Dividend"]
    assert section in valid_sections, f"Invalid section: {section}\n The section must be one of {valid_sections}\n Please specify a section from documentation"
    url = f"https://api.sectors.app/v1/companies/top/?classifications={section.replace(' ', '_').lower()}&n_stock={top_n}&year={year}&sub_sector={subsector.replace(' ', '-').lower()}"
    returned_data = _retrieve_from_endpoint(url)[f"{section.replace(' ', '_').lower()}"]
    if section in ["Revenue", "Earnings", "Market Cap"]:
        data = {"Symbol": [d["symbol"] for d in returned_data],
                "Company Name": [d["company_name"] for d in returned_data],
                f"{section} (Rp Trillion)": ["%.2f"%(d[f"{section.replace(' ', '_').lower()}"]/1e12) for d in returned_data]}
    elif section == "Dividend Yield":
        data = {"Symbol": [d["symbol"] for d in returned_data],
                "Company Name": [d["company_name"] for d in returned_data],
                "Dividend Yield (%)": ["%.2f"%(d["dividend_yield"]*100) for d in returned_data]}
    elif section == "Total Dividend":
        data = {"Symbol": [d["symbol"] for d in returned_data],
                "Company Name": [d["company_name"] for d in returned_data],
                "Total Dividend (Rp/Share)": ["%.2f"%(d["total_dividend"]) for d in returned_data]}
    df = pd.DataFrame(data)
    df = df.groupby(["Symbol", "Company Name"]).agg({df.columns[-1]:"mean"}).sort_values(df.columns[-1], ascending=False).reset_index()
    fig = simple_bar_chart(df=df, x_y_axis=["Symbol", df.columns[-1]], x_y_label=["Ticker Symbol", df.columns[-1]], chart_title=f"Top Companies by {section} in {subsector} subsector")
    return df.to_string(), st.plotly_chart(fig)

@tool
def top_gainers_losers(gainers_or_losers: Literal["top_gainers", "top_losers"], top_n: int, period: Literal["1d", "7d", "30d", "365d"], subsector: str) -> str:
    """
    Retrieve top-n gainers or losers stock price.
    Arg(s):
        - gainers_or_losers (Literal): Choices either top gainers or losers
        - top_n (int): The requested number (n) of top in a section
        - periode (Literal): Choices either 1d (daily), 7d (weekly), 30d (monthly), or 365d (yearly)
        - subsector (str): Choosen sub-sector in IDX
    Return(s):
        Stringed Pandas DataFrame contains top gainers or losers in a subsector
    """
    subsector = subsector.title()
    valid_subsectors = [d["subsector"].replace('-',' ').title() for d in helper_list_subsectors()]
    assert subsector in valid_subsectors, f"Invalid sub-sector: {subsector}\n The sub-sector must be one of {valid_subsectors}\n Please specify a sub-sector from documentation"

    url = f"https://api.sectors.app/v1/companies/top-changes/?classifications={gainers_or_losers}&n_stock={top_n}&periods={period}&sub_sector={subsector.replace(' ', '_').lower()}"
    returned_data = _retrieve_from_endpoint(url)
    data = {"Symbol": [d["symbol"] for d in returned_data[f"{gainers_or_losers}"][f"{period}"]],
            "Company Name" : [d["name"] for d in returned_data[f"{gainers_or_losers}"][f"{period}"]],
            "Price Change (%)": ["%.2f"%(d["price_change"]*100) for d in returned_data[f"{gainers_or_losers}"][f"{period}"]],
            f"Last Close Price in {returned_data[f'{gainers_or_losers}'][f'{period}'][0]['latest_close_date']} (Rp/Share)": [d["last_close_price"] for d in returned_data[f"{gainers_or_losers}"][f"{period}"]]}
    return pd.DataFrame(data).sort_values("Price Change (%)", ascending=False).reset_index().to_string()

@tool
def get_daily_trx(stock: str, start_date: str, end_date: str) -> Union[str, DeltaGenerator, list]:
    """
    Retrieve the daily transaction of a stock, including close price, volume, and market cap, within date range.

    Arg(s): 
        - stock (str) :  4-digits ticker stock of a company in IDX, e.g. BBRI
        - start_date (str): The start date of requested date range
        - end_date (str) : The end date of requested date range
    Return(s):
        - Stringed Pandas DataFrame contains top-n companies based on transaction volume within date range
        - Streamlit containter for plotly chart figure
        - List contains the skipped date because of either weekend or holidays
    """
    holiday_list = []
    while is_weekend_holiday(datetime.strptime(end_date, "%Y-%m-%d")) is True:
        holiday_list.append(f"{end_date} is either weekend or holiday")
        end_date = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        
    url = f"https://api.sectors.app/v1/daily/{stock}/?start={start_date}&end={end_date}"
    returned_data =  _retrieve_from_endpoint(url)
    data = {"Date": [d["date"] for d in returned_data],
            "Close Price (Rp/Share)" : [d["close"] for d in returned_data],
            "Volume (Shares)": [d["volume"] for d in returned_data],
            "Market Capitalization (Rp Trillion)": [d["market_cap"]/1e12 for d in returned_data]}
    df = pd.DataFrame(data)
    fig_close = simple_line_chart(df=df, x_y_label=["Date", "Close Price (Rp/Share)"], x_y_axis=["Date", "Close Price (Rp/Share)"], chart_title=f"Close Price of {stock} in {start_date} - {end_date}")
    fig_vol = simple_line_chart(df=df, x_y_label=["Date", "Volume (Shares)"], x_y_axis=["Date", "Volume (Shares)"], chart_title=f"Volume of {stock} in {start_date} - {end_date}")
    fig_market_cap = simple_line_chart(df=df, x_y_label=["Date", "Market Capitalization (Rp Trillion)"], x_y_axis=["Date", "Market Capitalization (Rp Trillion)"], chart_title=f"Market Cap of {stock} in {start_date} - {end_date}")
    return df.to_string(), st.plotly_chart(fig_close), st.plotly_chart(fig_vol), st.plotly_chart(fig_market_cap), holiday_list

@tool
def get_daily_trx_last_n_dates(stock: str, last_n_dates: int) -> Union[str, DeltaGenerator]:
    """
    Retrieve the daily transaction of a stock if the start and end dates not explicitly provided, i.e. requested the last n day(s) transactions.

    Arg(s): 
        - stock (str) :  4-digits ticker stock of a company in IDX, e.g. BBRI
        - last_n_dates (int) : Number for the requested last n days data
    Return(s):
        - Stringed Pandas DataFrame contains top-n companies based on transaction volume within date range
        - Streamlit containter for plotly chart figure
    """
    url = "https://api.sectors.app/v1/daily/{stock}/?start={get_last_n_dates(last_n_dates)['start_date']}&end={get_last_n_dates(last_n_dates)['end_date']}"
    returned_data = _retrieve_from_endpoint(url)
    data = {"Date": [d["date"] for d in returned_data],
            "Close Price (Rp/Share)" : [d["close"] for d in returned_data],
            "Volume (Shares)": [d["volume"] for d in returned_data],
            "Market Capitalization (Rp Trillion)": [d["market_cap"]/1e12 for d in returned_data]}
    df = pd.DataFrame(data)
    fig_close = simple_line_chart(df=df, x_y_label=["Date", "Close Price (Rp/Share)"], x_y_axis=["Date", "Close Price (Rp/Share)"], chart_title=f"Close Price of {stock} in {start_date} - {end_date}")
    fig_vol = simple_line_chart(df=df, x_y_label=["Date", "Volume (Shares)"], x_y_axis=["Date", "Volume (Shares)"], chart_title=f"Volume of {stock} in {start_date} - {end_date}")
    fig_market_cap = simple_line_chart(df=df, x_y_label=["Date", "Market Capitalization (Rp Trillion)"], x_y_axis=["Date", "Market Capitalization (Rp Trillion)"], chart_title=f"Market Cap of {stock} in {start_date} - {end_date}")
    return df.to_string(), st.plotly_chart(fig_close), st.plotly_chart(fig_vol), st.plotly_chart(fig_market_cap)

@tool
def get_historical_market_cap(start_date: str, end_date: str) -> Union[str, DeltaGenerator, list]:
    """
    Retrieve the historical daily market capitalization of the entire IDX within date range.

    Arg(s): 
        - start_date (str): The start date of requested date range
        - end_date (str) : The end date of requested date range
    Return(s):
        - Stringed Pandas DataFrame contains daily market capitalization of IDX within date range
        - Streamlit containter for plotly chart figure
        - List contains the skipped date because of either weekend or holidays
    """
    holiday_list = []
    while is_weekend_holiday(datetime.strptime(end_date, "%Y-%m-%d")) is True:
        holiday_list.append(f"{end_date} is either weekend or holiday")
        end_date = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://api.sectors.app/v1/idx-total/?start={start_date}&end={end_date}"
    returned_data =  _retrieve_from_endpoint(url)
    data = {"Date": [d["date"] for d in returned_data],
            "Market Capitalization (Rp Trillion)" : [d["idx_total_market_cap"]/1e12 for d in returned_data]}
    df = pd.DataFrame(data)
    fig = simple_line_chart(df=df, x_y_axis=["Date", "Market Capitalization (Rp Trillion)"], x_y_label=["Date", "Market Capitalization (Rp Trillion)"], chart_title="IDX Total Market Capitalization")
    return df.to_string(), st.plotly_chart(fig), holiday_list

@tool
def get_historical_market_cap_last_n_dates(last_n_dates: int) -> Union[str, DeltaGenerator]:
    """
    Retrieve the historical daily market capitalization of the entire IDX if the start and end dates not explicitly provided, i.e. requested the last n day(s) transactions.

    Arg(s): 
        - last_n_dates (int) : Number for the requested last n days data
    Return(s):
        - Stringed Pandas DataFrame contains daily market capitalization of IDX in the last n day(s)
        - Streamlit containter for plotly chart figure
    """
    url = f"https://api.sectors.app/v1/idx-total/?start={get_last_n_dates(last_n_dates)['start_date']}&end={get_last_n_dates(last_n_dates)['end_date']}"
    returned_data =  _retrieve_from_endpoint(url)
    data = {"Date": [d["date"] for d in returned_data],
            "Market Capitalization (Rp Trillion)" : [d["idx_total_market_cap"]/1e12 for d in returned_data]}
    df = pd.DataFrame(data)
    fig = simple_line_chart(df=df, x_y_axis=["Date", "Market Capitalization (Rp Trillion)"], x_y_label=["Date", "Market Capitalization (Rp Trillion)"], chart_title="IDX Total Market Capitalization")
    return df.to_string(), st.plotly_chart(fig)

@tool
def get_index_daily(index: str, start_date: str, end_date: str) -> Union[str, DeltaGenerator]:
    """
    Retrieve the historical daily market of an index within date range.

    Arg(s):
        - index (str): Choosen index in IDX 
        - start_date (str): The start date of requested date range
        - end_date (str) : The end date of requested date range
    Return(s):
        - Stringed Pandas DataFrame contains daily market of an index within date range
        - Streamlit container for plotly chart figure
    """
    valid_index = ["FTSE", "IDX30", "IDXBUMN20", "IDXESGL", "IDXG30", "IDXHIDIV20", "IDXQ30", "IDXV30", "IHSG", "JII70", "KOMPAS100", "LQ45", "SMINFRA18", "SRIKEHATI", "STI"]
    assert index.upper() in valid_index, f"Invalid index: {index}\n The index must be one of {valid_index}\n Please specify an index from documentation"

    url = f"https://api.sectors.app/v1/index-daily/{index}/?start={start_date}&end={end_date}"
    returned_data =  _retrieve_from_endpoint(url)
    data = {"Date": [d["date"] for d in returned_data],
            "Index Value" : [d["price"] for d in returned_data]}
    df = pd.DataFrame(data)
    fig = simple_line_chart(df=df, x_y_axis=["Date", "Index Value"], x_y_label=["Date", "Index Value"], chart_title=f"Daily Value of {index} within {start_date} - {end_date}")
    return df.to_string(), st.plotly_chart(fig)

@tool
def get_index_daily_last_n_dates(index:str, last_n_dates: int) -> Union[str, DeltaGenerator]:
    """
    Retrieve the historical daily market of an index if the start and end dates not explicitly provided, i.e. requested the last n day(s) an index transactions.

    Arg(s):
        - index (str): Choosen index in IDX  
        - last_n_dates (int) : Number for the requested last n days data
    Return(s):
        - Stringed Pandas DataFrame contains daily market of an index in the last n day(s)
        - Streamlit container for plotly chart figure]
    """
    valid_index = ["FTSE", "IDX30", "IDXBUMN20", "IDXESGL", "IDXG30", "IDXHIDIV20", "IDXQ30", "IDXV30", "JII70", "KOMPAS100", "LQ45", "SMINFRA18", "SRIKEHATI", "STI"]
    assert index.upper() in valid_index, f"Invalid index: {index}\n The index must be one of {valid_index}\n Please specify an index from documentation"

    url = f"https://api.sectors.app/v1/index-daily/{index}/?start={get_last_n_dates(last_n_dates)['start_date']}&end={get_last_n_dates(last_n_dates)['end_date']}"
    returned_data =  _retrieve_from_endpoint(url)
    data = {"Date": [d["date"] for d in returned_data],
            "Index Value" : [d["price"] for d in returned_data]}
    df = pd.DataFrame(data)
    fig = simple_line_chart(df=df, x_y_axis=["Date", "Index Value"], x_y_label=["Date", "Index Value"], chart_title=f"Daily Value of {index} in last {last_n_dates} day(s): within {get_last_n_dates(last_n_dates)['start_date']} - {get_last_n_dates(last_n_dates)['end_date']}")
    return df.to_string(), st.plotly_chart(fig)

@tool
def extract_from_list_of_dict(list_of_dict: list, extracted_key: str) -> list:
    """
    Tool for extracts values from list of dictionary due to most of the used data API is returned list of dictionary.

    Args(s):
        - list_of_dict (list): List of dictionary that returned from endpoint API
        - extracted_key (str): desired key to be exctract, e.g. "close"
    Return(s):
        a Python list contains values extracted
    """
    return [d[f'{extracted_key}'] for d in list_of_dict]

@tool
def addition(first_number:  Union[int, float], second_number: Union[int, float]) -> Union[int, float]:
    """
    Tool for addition between two numbers.
    If there are more than two numbers just add the rest behind.
    This tool could be used for financial data suming requests.

    Arg(s):
        - first_number (int|float): first number to add
        - second_number (int|float): second number to add with
    Return(s):
        a Python integer or float as the result of the addition operator
    """
    return first_number + second_number

@tool
def multiplication(first_number:  Union[int, float], second_number: Union[int, float]) -> Union[int, float]:
    """
    Tool for multiplication between two numbers.
    If there are more than two numbers just times the rest behind.

    Arg(s):
        - first_number (int|float): first number to times
        - second_number (int|float): second number to times with
    Return(s):
        a Python integer or float as the result of the multiplication operator
    """
    return first_number * second_number

@tool
def divition(first_number:  Union[int, float], second_number: Union[int, float]) -> Union[int, float]:
    """
    Tool for divition between two numbers.
    If there are more than two numbers just divide the rest behind.

    Arg(s):
        - first_number (int|float): first number to divide
        - second_number (int|float): second number to divide with
    Return(s):
        a Python integer or float as the result of the divition operator
    """
    return first_number / second_number

@tool
def power(first_number:  Union[int, float], second_number: Union[int, float]) -> Union[int, float]:
    """
    Tool for power between two numbers.
    If there are more than two numbers just power the rest behind.

    Arg(s):
        - first_number (int|float): first number to power
        - second_number (int|float): second number to power with
    Return(s):
        a Python integer or float as the result of the power operator
    """
    return first_number ^ second_number

@tool
def power_root(number:  Union[int, float], root: Union[int, float]=2) -> Union[int, float]:
    """
    Tool for power root

    Arg(s):
        - number (int|float): The number to power root
        - power_root (int|float): The power root, default to 2, i.e root square
    Return(s):
        a Python integer or float as the result of the power root operator
    """
    return number ** (1/root)

@tool
def suming(list_of_numbers: list) -> Union[int, float]:
    """
    Tool for get the sum of some numbers.
    This tool could be used for financial data suming requests.

    Args(s):
        - list_of_numbers (list): List that contains some numbers to sum
    Return(s):
        a Python integer or float as the result of sum
    """
    return sum(list_of_numbers)

@tool
def average(list_of_numbers: list) -> Union[int, float]:
    """
    Tool for get the average of some numbers.
    This tool could be used for financial data averaging requests.

    Args(s):
        - list_of_numbers (list): List that contains some numbers to average
    Return(s):
        a Python integer or float as the result of average
    """
    return sum(list_of_numbers)/len(list_of_numbers)

@tool
def which_greater(first_number:  Union[int, float], second_number: Union[int, float]) -> str:
    """
    Tool for compare two numbers, which one is greater between the first number and the second number

    Arg(s):
        - first_number (int|float): first number to compare
        - second_number (int|float): second number to compare with
    Return(s):
        a Python string that result which one is greater
    """
    if first_number > second_number:
        return first_number
    elif first_number < second_number:
        return second_number
    
# Build a class for chat agent
class ChatAgent:
    def __init__(self, chat_input: str):
        self.chat_input = chat_input

    def __repr__(self):
        return f"Answer: {self._execute_agent()}"

    def tools_list(self):
        return [list_subsectors,
                list_industries,
                list_subindustries,
                list_companies_by_subsectors,
                list_companies_by_subindustries,
                list_companies_by_index,
                companies_performance_since_ipo,
                get_company_info,
                get_top_companies_by_trx_volume,
                get_top_companies_by_trx_volume_last_n_dates,
                get_top_companies_by_section,
                top_gainers_losers,
                get_daily_trx,
                get_daily_trx_last_n_dates,
                get_historical_market_cap,
                get_historical_market_cap_last_n_dates,
                get_index_daily,
                get_index_daily_last_n_dates,
                extract_from_list_of_dict,
                addition,
                multiplication,
                divition,
                power,
                power_root,
                suming,
                average,
                which_greater]     
    
    def _set_agent(self):
        tools = self.tools_list()

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                   "system",
                    f"""Answer in Indonesian or English depending which language is used in "{input}".
                    You are a helpful assistant with access to several tools for retrieving financial data in IDX (Indonesia), therefore just answering in IDX-scope, not other countries exchange. 
                    Answer the following questions, being as factual and analytical as you can, the data is provided to you through the tools.
                    If the user ask from some data, display it in pretty and properly ways, if the data consist of more than one column use the table properly.
                    For `get_top_companies_by_trx_volume()` and `get_top_companies_by_trx_volume_last_n_dates()` if the user does not mention a subsector, the subsector parameter is by default set to None.
                    If there are holiday_list in the function return, tell to the user that there are either weekends or holidays within the requested date range.
                    For the decimal/numerical answer, round up to 2-digits after decimal.
                    For all the table format display you must be provide the number row index, start from 1, as first column on the left.
                    Today date is {datetime.today().strftime('%Y-%m-%d')}.
                    """
                ),
                (
                    "human", "{input}",
                ),
                MessagesPlaceholder("agent_scratchpad")  
            ]
        )

        llm = ChatGroq(
            model_name="llama3-70b-8192",
            temperature=0,
            groq_api_key=GROQ_API_KEY
        )
        return create_tool_calling_agent(llm, tools, prompt)
    
    def _execute_agent(self):
        agent = self._set_agent()
        agent_executor =  AgentExecutor(agent=agent, tools=self.tools_list(), verbose=True)
        result = agent_executor.invoke({"input": self.chat_input})
        return result["output"]