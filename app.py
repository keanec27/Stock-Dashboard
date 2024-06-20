import requests
import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np

st.set_page_config(layout="wide",page_title="Stock Dashboard",page_icon="📈",initial_sidebar_state="collapsed")
st.html("styles.html")
   
def configure():
    load_dotenv()
  
@st.cache_data
def get_stock_price(ticker):
    # key = os.getenv('api_key')   # Uncomment this line if you are using .env file and comment the next line
    key = st.secrets['api_key']  # Uncomment this line if you are using Streamlit secrets
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={key}&datatype=csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['timestamp'])
    df.drop('timestamp',axis=1,inplace=True)
    df = pd.read_excel('Stock Dashboard.xlsx',sheet_name='AAPL')
    return df
     
# @st.experimental_fragment   # Runs the required function only when select box value changes and not the entire script
def display_symbol_history():
    left_widget, right_widget, _ = st.columns([1,1,1.5])
    companies = pd.read_csv('listing_status.csv')
    comp = companies[companies['assetType']=="Stock"]['symbol'].to_list()
    ticker = left_widget.selectbox("📊 Currently Showing",comp,placeholder='Search',index=None)
    period = right_widget.selectbox('🕗Period',["Week","Month","Trimester","Quarter","Year"],placeholder="Select Period",index=None)
    
    if period and ticker: 
        mapping_period = {"Week": 7, "Month": 31,"Trimester": 90,"Quarter": 120, "Year": 365}
        today = datetime.today().date()
        today = pd.to_datetime(today)
        
        df = get_stock_price(ticker)
        today = datetime(2024,4,19) # For testing purposes
        
        df['Date'] = pd.to_datetime(df['Date'],dayfirst=True)
        df = df.set_index('Date')
        df = df[(today - pd.Timedelta(mapping_period[period], unit='d')) : today]
        
        f_candle = plot_candlestick(df)
        
        left_chart, right_indicator = st.columns([1.5,1])

        with left_chart:
            st.plotly_chart(f_candle,use_container_width=True)
        with right_indicator:
            st.subheader("Period Metrics")
            l,r = st.columns(2)
            with l:
                st.html('<span class="low_indicator"></span>')
                st.metric("Lowest Volume Day Trade",
                        f'{df["Volume"].min():,}',)
                st.metric("Lowest Close Day Trade",
                        f'{df["Close"].min():,}',)
            with r:
                st.html('<span class="high_indicator"></span>')
                st.metric("Highest Volume Day Trade",
                        f'{df["Volume"].max():,}',)
                st.metric("Highest Close Day Trade",
                        f'{df["Close"].max():,}',)
            with st.container():
                st.html('<span class="bottom_indicator"></span>')
                st.metric('Average Daily Volume',
                        f'{int(df["Volume"].mean()):,}',)
        
def plot_candlestick(df):
    f_candle = make_subplots(rows=2, cols=1,shared_xaxes=True,vertical_spacing=0.1,row_heights=[0.7,0.3])
    
    f_candle.add_trace(
        go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Candlestick'),row=1,col=1)
    f_candle.add_trace(
        go.Bar(x=df.index,y=df['Volume'],name='Volume Traded'),row=2,col=1)
    f_candle.update_layout(title='Stock Price Trends',
                           showlegend=True,
                           xaxis_rangeslider_visible=False,
                           yaxis1=dict(title='OHLC'),
                           yaxis2=dict(title='Volume'),
                           hovermode='x',
                            )
    f_candle.update_layout(title_font_family='Open Sans',
                           title_font_color='#174C4F',
                           title_font_size=32,
                           font_size=16,
                           margin = dict(l=80,r=80,t=100,b=80, pad=0),
                           height = 500,                        
                           )
    return f_candle


st.html('<h1 class="title">Stock Dashboard</h1>')

display_symbol_history()

