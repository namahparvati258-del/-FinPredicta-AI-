import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go

# Professional Page Setup
st.set_page_config(page_title="FinPredicta AI", layout="wide")
st.title("📈 FinPredicta: AI-Powered Investment Advisor")

# --- STEP 1: DATE SELECTION (Moved to main area to avoid pop-up issues) ---
st.subheader("Step 1: Select Time Period")
col_d1, col_d2 = st.columns(2)

with col_d1:
    # Start Date: Default to 1 year ago, but allow user to go back to year 2000
    start_date = st.date_input("Start Date", 
                              value=datetime.date.today() - datetime.timedelta(days=365),
                              min_value=datetime.date(2000, 1, 1))
with col_d2:
    # End Date: Default to today
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
    ticker_symbol = st.text_input("Enter Company Symbol (e.g., RELIANCE.NS, TSLA, BTC-USD):", "RELIANCE.NS")
    search_list = [ticker_symbol.upper()]
else:
    selected_sector = st.selectbox("Select a Sector:", list(sectors.keys()))
    search_list = sectors[selected_sector]

# --- STEP 3: INVESTMENT ---
st.subheader("Step 3: Investment Amount")
# Clean text input to avoid +/- buttons
invest_input = st.text_input("Enter amount to invest (e.g., 5000):", "1000")
try:
    investment_amount = float(invest_input)
except:
    investment_amount = 0

# --- ANALYSIS ---
if st.button("Calculate Growth"):
    if start_date >= end_date:
        st.error("Error: Start Date must be before the End Date.")
    elif investment_amount <= 0:
        st.error("Please enter a valid investment amount.")
    else:
        results = []
        with st.spinner('Analyzing market data...'):
            for sym in search_list:
                # Fetching data
                data = yf.download(sym, start=start_date, end=end_date)
                if not data.empty:
                    # Clean data extraction
                    s_price = float(data['Close'].iloc[0])
                    e_price = float(data['Close'].iloc[-1])
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
            
            st.success(f"Best Performer in selected period: **{top_asset['Asset']}**")
            
            # Show Metric
            final_val = investment_amount * (1 + top_asset['Growth (%)']/100)
            st.metric(f"Your {investment_amount} would have become:", f"{final_val:,.2f}", f"{top_asset['Growth (%)']}%")
            
            # Show Table and Graph
            col_left, col_right = st.columns([1, 2])
            with col_left:
                st.write("### Data Table")
                st.dataframe(df, use_container_width=True)
            
            with col_right:
                # Fetching data again for the graph to ensure it's clean
                plot_data = yf.download(top_asset['Asset'], start=start_date, end=end_date)
                if not plot_data.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=plot_data.index, 
                        y=plot_data['Close'], 
                        mode='lines', 
                        name=top_asset['Asset'],
                        line=dict(color='#00d1b2', width=3) # Bright teal color for visibility
                    ))
                    fig.update_layout(
                        title=f"Price Trend: {top_asset['Asset']}",
                        template="plotly_dark", # Dark theme for professional look
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="Date",
                        yaxis_title="Price"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found. This happens if the market was closed or the symbol is incorrect.")

st.markdown("---")
st.caption("FinPredicta - Simple Financial Analysis for Everyone")