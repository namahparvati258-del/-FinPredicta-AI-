import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go
import numpy as np

# Page Setup
st.set_page_config(page_title="FinPredicta AI", layout="wide")
st.title("📈 FinPredicta: AI-Powered Investment Advisor")

# --- STEP 1: DATE SELECTION ---
st.subheader("Step 1: Select Time Period")
col_d1, col_d2 = st.columns(2)
with col_d1:
    start_date = st.date_input("Start Date", 
                              value=datetime.date.today() - datetime.timedelta(days=365),
                              min_value=datetime.date(2000, 1, 1))
with col_d2:
    end_date = st.date_input("End Date", value=datetime.date.today())

# --- STEP 2: ASSET SELECTION ---
st.subheader("Step 2: Choose Asset")
search_mode = st.radio("Search Preference:", ["Sector Comparison", "Single Asset Search"], horizontal=True)

sectors = {
    "Petroleum & Energy": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "XOM"],
    "Banking & Finance": ["HDFCBANK.NS", "ICICIBANK.NS", "SBI.NS", "JPM"],
    "IT & Technology": ["TCS.NS", "INFY.NS", "AAPL", "GOOGL", "NVDA"],
    "Cryptocurrency": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "Automobile": ["TATAMOTORS.NS", "M&M.NS", "F", "TM"]
}

if search_mode == "Single Asset Search":
    ticker_symbol = st.text_input("Enter Company Symbol:", "RELIANCE.NS")
    search_list = [ticker_symbol.upper()]
else:
    selected_sector = st.selectbox("Select a Sector:", list(sectors.keys()))
    search_list = sectors[selected_sector]

# --- STEP 3: INVESTMENT ---
st.subheader("Step 3: Investment Amount")
invest_input = st.text_input("Enter amount to invest:", "1000")
try:
    investment_amount = float(invest_input)
except:
    investment_amount = 0

# --- ANALYSIS ---
if st.button("Calculate Growth"):
    if start_date >= end_date:
        st.error("Error: Start Date must be before End Date.")
    elif investment_amount <= 0:
        st.error("Please enter a valid amount.")
    else:
        results = []
        with st.spinner('Analyzing market data...'):
            for sym in search_list:
                # auto_adjust=True removes extra column layers
                data = yf.download(sym, start=start_date, end=end_date, auto_adjust=True)
                
                if not data.empty and len(data) > 1:
                    # FIX: Converting to numpy array and flattening to get the pure number
                    close_prices = data['Close'].values.flatten()
                    s_price = float(close_prices[0])
                    e_price = float(close_prices[-1])
                    
                    growth = ((e_price - s_price) / s_price) * 100
                    results.append({
                        "Asset": sym, 
                        "Growth (%)": round(growth, 2), 
                        "Price at Start": round(s_price, 2),
                        "Price at End": round(e_price, 2)
                    })

        if results:
            df = pd.DataFrame(results).sort_values(by="Growth (%)", ascending=False)
            top_asset = df.iloc[0]
            st.success(f"Best Performer: {top_asset['Asset']}")
            
            final_val = investment_amount * (1 + top_asset['Growth (%)']/100)
            st.metric(f"Your {investment_amount} would become:", f"{final_val:,.2f}", f"{top_asset['Growth (%)']}%")
            
            col_left, col_right = st.columns([1, 2])
            with col_left:
                st.write("### Comparison Table")
                st.dataframe(df, use_container_width=True)
            with col_right:
                # Re-fetching for a clean graph
                plot_data = yf.download(top_asset['Asset'], start=start_date, end=end_date, auto_adjust=True)
                if not plot_data.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['Close'].values.flatten(), 
                                             mode='lines', line=dict(color='#00d1b2', width=3)))
                    fig.update_layout(template="plotly_dark", 
                                      title=f"Price Trend: {top_asset['Asset']}",
                                      xaxis_title="Date", yaxis_title="Price")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found. Try a different date range or symbol.")