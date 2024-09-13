# Import package(s)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta 

from st_pages import hide_pages
# Set page configuration
st.set_page_config(page_title="RFin", layout="wide", 
                   page_icon="pages/assets/rf_logo.png",
                   initial_sidebar_state="collapsed",
                   menu_items={'About': "RFin is a Simple IDX Stocks Dashboard"})

def _retrieve_from_endpoint(url: str):
    """
    Retrieve the financial data from the Sectors API according to the url.

    Arg(s): 
        - url (str): The url to Sectors API hit
    Return(s):
        a Python string that contains requested financial data
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def simple_line_chart(df: pd.DataFrame, x_y_axis: list, x_y_label: list = None, chart_title: str = None, markers: bool = False):
    """
    A helper function to get a simple line chart figure using Plotly Express.

    Arg(s):
        - df (DataFrame): a dataframe contains 2 columns data for line chart
        - x_y_axis (list): a list for x and y axis name
        - x_y_label (list): a list for x and y axis label display in chart
        - chart_title (str): desired chart title
    """
    return px.line(df, x=x_y_axis[0], y=x_y_axis[1], template="ggplot2", title=chart_title, labels={x_y_axis[0]: x_y_label[0], x_y_axis[1]:x_y_label[1]}, line_shape="spline", markers=markers)

def simple_candlestick(df: pd.DataFrame, x_y_label: list = None, chart_title: str = None):
    """
    A helper function to get a simple candlestick figure using Plotly.

    Arg(s):
        - df (DataFrame): a dataframe contains 6 columns data for candlestick, i.e. date, open, high, low, close, volume
        - x_y_label (list): a list for x and y axis label display in chart
        - chart_title (str): desired chart title
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
               vertical_spacing=0.03, subplot_titles=("OHLC", "Volume"), 
               row_width=[0.2, 0.7])
    fig.add_trace(go.Candlestick(x=df["date"], open=df["open"], high=df["high"],
                low=df["low"], close=df["close"], name="OHLC"), 
                row=1, col=1)
    fig.add_trace(go.Bar(x=df['date'], y=df['volume'], showlegend=False), row=2, col=1)
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_xaxes(
    rangebreaks=[
        { 'pattern': 'day of week', 'bounds': [6, 1]}
    ])
    return fig

st.title("RFin - IDX Mini Dashboard") 
col1, col2 = st.columns(2)
with col1:
    st.header("Indonesia Stock Exchange (IDX) Total Market Capitalization")
    tabs = st.tabs(["2 Weeks", "1 Month", "3 Months"])
    with tabs[0]:
        returned_data = _retrieve_from_endpoint(f"http://127.0.0.1:8000/api/idx-total-market-cap?start_date={(datetime.today() + relativedelta(weeks=-2)).strftime('%Y-%m-%d')}")
        data = {"Date": [d["date"] for d in returned_data],
                "Market Capitalization (Rp Trillion)" : [d["idx_total_market_cap"]/1e12 for d in returned_data]}
        idx_df = pd.DataFrame(data)
        fig = simple_line_chart(df=idx_df, x_y_axis=["Date", "Market Capitalization (Rp Trillion)"], x_y_label=["Date", "Market Capitalization (Rp Trillion)"])
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        returned_data = _retrieve_from_endpoint(f"http://127.0.0.1:8000/api/idx-total-market-cap?start_date={(datetime.today() + relativedelta(months=-1)).strftime('%Y-%m-%d')}")
        data = {"Date": [d["date"] for d in returned_data],
                "Market Capitalization (Rp Trillion)" : [d["idx_total_market_cap"]/1e12 for d in returned_data]}
        idx_df = pd.DataFrame(data)
        fig = simple_line_chart(df=idx_df, x_y_axis=["Date", "Market Capitalization (Rp Trillion)"], x_y_label=["Date", "Market Capitalization (Rp Trillion)"])
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        returned_data = _retrieve_from_endpoint(f"http://127.0.0.1:8000/api/idx-total-market-cap?start_date={(datetime.today() + relativedelta(months=-3)).strftime('%Y-%m-%d')}")
        data = {"Date": [d["date"] for d in returned_data],
                "Market Capitalization (Rp Trillion)" : [d["idx_total_market_cap"]/1e12 for d in returned_data]}
        idx_df = pd.DataFrame(data)
        fig = simple_line_chart(df=idx_df, x_y_axis=["Date", "Market Capitalization (Rp Trillion)"], x_y_label=["Date", "Market Capitalization (Rp Trillion)"])
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.header("Movement of Index in IDX")
    selected_index = st.selectbox("Choose an index", ["FTSE", "IDX30", "IDXBUMN20", "IDXESGL", "IDXG30", "IDXHIDIV20", "IDXQ30", "IDXV30", "IHSG", "JII70", "KOMPAS100", "LQ45", "SRI-KEHATI", "STI"], index=8)
    returned_data = _retrieve_from_endpoint(f"http://127.0.0.1:8000/api/index-daily?index_code={selected_index}")
    data = {"Date": [d["date"] for d in returned_data],
            "Price": [d["price"] for d in returned_data]}
    index_df = pd.DataFrame(data).sort_values("Date", ascending=True)
    tabs = st.tabs(["2 Weeks", "1 Month", "3 Months"])
    with tabs[0]:
        fig = simple_line_chart(df=index_df[index_df["Date"] >= (datetime.today() + relativedelta(weeks=-2)).strftime('%Y-%m-%d')], x_y_axis=["Date", "Price"],  x_y_label=['Date', ' '])
        st.plotly_chart(fig, use_container_width=True)
    with tabs[1]:
        fig = simple_line_chart(df=index_df[index_df["Date"] >= (datetime.today() + relativedelta(months=-1)).strftime('%Y-%m-%d')], x_y_axis=["Date", "Price"],  x_y_label=['Date', ' '])
        st.plotly_chart(fig, use_container_width=True)
    with tabs[2]:
        fig = simple_line_chart(df=index_df[index_df["Date"] >= (datetime.today() + relativedelta(months=-3)).strftime('%Y-%m-%d')], x_y_axis=["Date", "Price"],  x_y_label=['Date', ' '])
        st.plotly_chart(fig, use_container_width=True)

ticker_list = [f"{d['symbol']} | {d['company_name']}" for d in _retrieve_from_endpoint("http://127.0.0.1:8000/api/ticker-list")]
selected_ticker = st.selectbox(label="Type or dropdown a stock symbol here, e.g. BBRI or Bank Rakyat Indonesia", options=ticker_list)

st.header(f"{str(selected_ticker)[:7]} Overview")
returned_data = _retrieve_from_endpoint(f"http://127.0.0.1:8000/api/ticker-overview?symbol={str(selected_ticker)[:7]}")
get_dict = returned_data[0]
company_info = {
    "Symbol": get_dict["symbol"],
    "Company Name": get_dict["company_name"],
    "Sector": get_dict["sector"],
    "Sub-Sector": get_dict["sub_sector"],
    "Industry": get_dict["sub_industry"],
    "Listing Date": get_dict["listing_date"],
    "Website": get_dict["website"]
}
st.markdown("""
<style>
.info-box {
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}
.info-key {
    font-weight: bold;
    color: #333;
}
.info-value {
    color: #555;
}
</style>
""", unsafe_allow_html=True)

for key, value in company_info.items():
    st.markdown(f"""
    <div class="info-box">
        <span class="info-key">{key}:</span> <span class="info-value">{value}</span>
    </div>
    """, unsafe_allow_html=True)

st.header(f"{str(selected_ticker)[:7]} Prices Movement")
returned_data = _retrieve_from_endpoint(f"http://127.0.0.1:8000/api/ticker-daily?symbol={str(selected_ticker)[:7]}")
data = {"date": [d["date"] for d in returned_data],
        "symbol": [d["symbol"] for d in returned_data],
        "open": [d["open"] for d in returned_data],
        "high": [d["high"] for d in returned_data],
        "low": [d["low"] for d in returned_data],
        "close": [d["close"] for d in returned_data],
        "volume": [d["volume"] for d in returned_data]}
ticker_daily_df = pd.DataFrame(data)
ticker_daily_df['date'] = pd.to_datetime(ticker_daily_df['date'])
tabs = st.tabs(["2 Weeks", "1 Month", "3 Months"])
with tabs[0]:
    fig = simple_candlestick(df=ticker_daily_df[ticker_daily_df["date"] >= (datetime.today() + relativedelta(weeks=-2)).strftime('%Y-%m-%d')], x_y_label=["Date", "Price (Rp/Share)"])
    st.plotly_chart(fig, use_container_width=True)
with tabs[1]:
    fig = simple_candlestick(df=ticker_daily_df[ticker_daily_df["date"] >= (datetime.today() + relativedelta(months=-1)).strftime('%Y-%m-%d')], x_y_label=["Date", "Price (Rp/Share)"])
    st.plotly_chart(fig, use_container_width=True)
with tabs[2]:
    fig = simple_candlestick(df=ticker_daily_df[ticker_daily_df["date"] >= (datetime.today() + relativedelta(months=-3)).strftime('%Y-%m-%d')], x_y_label=["Date", "Price (Rp/Share)"])
    st.plotly_chart(fig, use_container_width=True)

st.header(f"{str(selected_ticker)[:7]} Financial Informations")
col1, col2, col3 = st.columns(3)
with col1:
    returned_data = _retrieve_from_endpoint(f"http://127.0.0.1:8000/api/income-statement?symbol={str(selected_ticker)[:7]}")
    data = {"Year": [d["year"] for d in returned_data],
        "Total Revenue (Rp Billion)": [d["total_revenue"]/1e9 for d in returned_data],
        "Net Income (Rp Billion)": [d["net_income"]/1e9 for d in returned_data],
        "NPM (%)": [(d["net_income"]/d["total_revenue"])*100 if d["total_revenue"] != 0 else 0 for d in returned_data]}
    if not data["Year"] or not data["Total Revenue (Rp Billion)"] or not data["Net Income (Rp Billion)"] or not data["NPM (%)"]:
        fig = go.Figure()
        fig.add_annotation(
            text="No Data Available",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=20),
            x=0.5, y=0.5,  # Center the text
            xanchor='center', yanchor='middle'
        )
        fig.update_layout(
            title={"text": "Income Statement", "x":0.5, "xanchor": "center", "yanchor": "top"},
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="white",
            margin=dict(t=100, b=70))
    else:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=data['Year'], y=data['NPM (%)'], mode='lines+markers', name='NPM'),
            secondary_y=True
        )
        fig.add_trace(
            go.Bar(x=data['Year'], y=data['Total Revenue (Rp Billion)'], name='Total Revenue'),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(x=data['Year'], y=data['Net Income (Rp Billion)'], name='Net Income'),
            secondary_y=False
        )
        fig.update_layout(
            title={"text": "Income Statement", "x":0.5, "xanchor": "center", "yanchor": "top"},
            xaxis_title="Year",
            yaxis_title="Total (Rp Billion)",
            yaxis2_title="Net Profit Margin (%)",
            barmode='group',  
            legend=dict(orientation='h', x=0.5, y=1.1, xanchor='center', yanchor='bottom'),
            margin=dict(t=150, b=70))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    returned_data = _retrieve_from_endpoint(f"http://127.0.0.1:8000/api/balance-sheet?symbol={str(selected_ticker)[:7]}")
    data = {"Year": [d["year"] for d in returned_data],
        "Assets (Rp Trillion)": [d["assets"]/1e12 for d in returned_data],
        "Liabilities (Rp Trillion)": [d["liabilities"]/1e12 for d in returned_data],
        "Equity (Rp Trillion)": [(d["assets"] - d["liabilities"])/1e12 for d in returned_data],
        "DER (%)": [(d["liabilities"]/(d["assets"] - d["liabilities"]))*100 if (d["assets"] - d["liabilities"]) != 0 else 0 for d in returned_data]}
    if not data["Year"] or not data["Assets (Rp Trillion)"] or not data["Liabilities (Rp Trillion)"] or not data["Equity (Rp Trillion)"] or not data["DER (%)"]:
        fig = go.Figure()
        fig.add_annotation(
            text="No Data Available",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=20),
            x=0.5, y=0.5,  # Center the text
            xanchor='center', yanchor='middle'
        )
        fig.update_layout(
            title={"text": "Cash Flow", "x":0.5, "xanchor": "center", "yanchor": "top"},
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="white",
            margin=dict(t=100, b=70))
    else:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=data['Year'], y=data['DER (%)'], mode='lines+markers', name='DER'),
            secondary_y=True
        )
        fig.add_trace(
            go.Bar(x=data['Year'], y=data['Assets (Rp Trillion)'], name='Assets'),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(x=data['Year'], y=data['Liabilities (Rp Trillion)'], name='Liabilities'),
            secondary_y=False
        )
        fig.update_layout(
            title={"text": "Balance Sheet", "x":0.5, "xanchor": "center", "yanchor": "top"},
            xaxis_title="Year",
            yaxis_title="Total (Rp Trillion)",
            yaxis2_title="Debt-to-Equity Ratio (%)",
            barmode='group',  
            legend=dict(orientation='h', x=0.5, y=1.1, xanchor='center', yanchor='bottom'),
            margin=dict(t=150, b=70))
    st.plotly_chart(fig, use_container_width=True)

with col3:
    returned_data = _retrieve_from_endpoint(f"http://127.0.0.1:8000/api/cash-flow?symbol={str(selected_ticker)[:7]}")
    data = {"Year": [d["year"] for d in returned_data],
        "Operating Cash Flow (Rp Billion)": [d["operating_cf"]/1e9 for d in returned_data],
        "Investing Cash Flow (Rp Billion)": [d["investing_cf"]/1e9 for d in returned_data],
        "Financing Cash Flow (Rp Billion)": [d["financing_cf"]/1e9 for d in returned_data]}
    if not data["Year"] or not data["Operating Cash Flow (Rp Billion)"] or not data["Investing Cash Flow (Rp Billion)"] or not data["Financing Cash Flow (Rp Billion)"]:
        fig = go.Figure()
        fig.add_annotation(
            text="No Data Available",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=20),
            x=0.5, y=0.5,  # Center the text
            xanchor='center', yanchor='middle'
        )
        fig.update_layout(
            title={"text": "Cash Flow", "x":0.5, "xanchor": "center", "yanchor": "top"},
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="white",
            margin=dict(t=100, b=70))
    else:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=data['Year'], y=data['Operating Cash Flow (Rp Billion)'], name='Operating Cash Flow'),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(x=data['Year'], y=data['Investing Cash Flow (Rp Billion)'], name='Investing Cash Flow'),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(x=data['Year'], y=data['Financing Cash Flow (Rp Billion)'], name='Financing Cash Flow'),
            secondary_y=False
        )
        # Update layout for the figure
        fig.update_layout(
            title={"text": "Cash Flow", "x":0.5, "xanchor": "center", "yanchor": "top"},
            xaxis_title="Year",
            yaxis_title="Total (Rp Billion)",
            barmode='group',  
            legend=dict(orientation='h', x=0.5, y=1.1, xanchor='center', yanchor='bottom'),
            margin=dict(t=150, b=70))
    st.plotly_chart(fig, use_container_width=True)

if st.sidebar.button("Log Out"):
    del st.session_state["access"]
    st.switch_page("app.py")
    hide_pages(["RFin Mini Dashboard", "RFin AI-ChatBot"])