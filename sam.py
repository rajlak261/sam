import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

st.set_page_config(page_title="📈 Enhanced Stock Dashboard", layout="wide")
st.title("📊 Real-Time Stock Dashboard with Portfolio Tracker")

# Sidebar selection
symbols = st.sidebar.multiselect(
    "Select Stocks to View",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "IBM", "INTC"],
    default=["AAPL", "TSLA"]
)
start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# Portfolio input
st.sidebar.subheader("📦 Portfolio Tracker")
portfolio = {}
for symbol in symbols:
    shares = st.sidebar.number_input(f"{symbol} shares", min_value=0, step=1, key=f"shares_{symbol}")
    portfolio[symbol] = shares

# Alert input
st.sidebar.subheader("🔔 Price Alerts")
alerts = {}
for symbol in symbols:
    alert_price = st.sidebar.number_input(f"Alert if {symbol} > $", min_value=0.0, step=1.0, key=f"alert_{symbol}")
    alerts[symbol] = alert_price

# Load data
if symbols:
    data = yf.download(symbols, start=start_date, end=end_date, group_by='ticker', auto_adjust=True)

    # Price chart
    st.subheader("📈 Closing Price Trend")
    fig1 = go.Figure()
    for symbol in symbols:
        if len(symbols) == 1:
            fig1.add_trace(go.Scatter(x=data.index, y=data["Close"], mode='lines', name=symbol))
        else:
            fig1.add_trace(go.Scatter(x=data[symbol].index, y=data[symbol]["Close"], mode='lines', name=symbol))
    fig1.update_layout(xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig1, use_container_width=True)

    # Volume chart
    st.subheader("📊 Volume Traded")
    fig2 = go.Figure()
    for symbol in symbols:
        if len(symbols) == 1:
            fig2.add_trace(go.Scatter(x=data.index, y=data["Volume"], mode='lines', name=symbol))
        else:
            fig2.add_trace(go.Scatter(x=data[symbol].index, y=data[symbol]["Volume"], mode='lines', name=symbol))
    fig2.update_layout(xaxis_title="Date", yaxis_title="Volume")
    st.plotly_chart(fig2, use_container_width=True)

    # Portfolio value
    st.subheader("💼 Portfolio Value")
    prices_now = yf.download(symbols, period='1d')['Close'].iloc[-1]
    total_value = 0
    for symbol in symbols:
        price = prices_now if isinstance(prices_now, float) else prices_now[symbol]
        value = price * portfolio[symbol]
        total_value += value
        st.write(f"{symbol}: {portfolio[symbol]} × ${price:.2f} = ${value:.2f}")
    st.success(f"📊 Total Portfolio Value: ${total_value:,.2f}")

    # Alerts
    st.subheader("🔔 Alerts")
    for symbol in symbols:
        price = prices_now if isinstance(prices_now, float) else prices_now[symbol]
        if alerts[symbol] > 0 and price > alerts[symbol]:
            st.warning(f"🚨 {symbol} crossed ${alerts[symbol]:.2f} → Current: ${price:.2f}")

    # Candlestick with SMA
    st.subheader("🕯 Candlestick Chart with 20-Day SMA")
    for symbol in symbols:
        df = yf.download(symbol, start=start_date, end=end_date)
        df["SMA20"] = df["Close"].rolling(window=20).mean()
        fig = go.Figure(data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Candlestick"
            ),
            go.Scatter(
                x=df.index,
                y=df["SMA20"],
                line=dict(color='orange', width=1.5),
                name="20-Day SMA"
            )
        ])
        fig.update_layout(title=f"{symbol} Candlestick with SMA", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("👈 Please select at least one stock.")
