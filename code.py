import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go

# Page Setup
st.set_page_config(page_title="FinPredicta AI", layout="wide")
st.title("📈 FinPredicta: AI-Powered Investment Advisor")
st.write("Analyze global stocks and see how much your money can grow!")

# --- SIDEBAR ---
st.sidebar.header("Step 1: Select Time Period")
today = datetime.date.today()
start_date = st.sidebar.date_input("Start Date", today - datetime.timedelta(days=365))
end_date = st.sidebar.date_input("End Date", today)

# --- MAIN SECTION ---
st.subheader("Step 2: Choose Asset")
search_mode = st.radio("Mode:", ["Sector Comparison", "Single Asset Search"])

sectors = {
    "Petroleum & Energy": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "XOM", "CVX"],
    "Banking & Finance": ["HDFCBANK.NS", "ICICIBANK.NS", "SBI.NS", "JPM", "BAC"],
    "IT & Technology": ["TCS.NS", "INFY.NS", "AAPL", "GOOGL", "MSFT", "NVDA"],
    "Cryptocurrency": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "Automobile": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "F", "TM"]
}

if search_mode == "Single Asset Search":
    ticker_symbol = st.text_input("Enter Symbol (e.g. RELIANCE.NS):", "RELIANCE.NS")
    search_list = [ticker_symbol.upper()]
else:
    selected_sector = st.selectbox("Select Sector:", list(sectors.keys()))
    search_list = sectors[selected_sector]

st.subheader("Step 3: Investment Amount")
# FIX: Using text_input to avoid +/- buttons
invest_input = st.text_input("How much money do you want to invest? (Type amount):", "1000")
investment_amount = float(invest_input) if invest_input.isdigit() else 0

if st.button("Start Analysis"):
    if start_date >= end_date:
        st.error("Error: Start Date must be before End Date.")
    elif investment_amount <= 0:
        st.error("Please enter a valid investment amount.")
    else:
        results = []
        with st.spinner('Fetching data...'):
            for sym in search_list:
                data = yf.download(sym, start=start_date, end=end_date)
                if not data.empty:
                    # FIX: Using .iloc[0].item() to get clean numeric value
                    start_p = data['Close'].iloc[0]
                    end_p = data['Close'].iloc[-1]
                    
                    # Convert to float to avoid calculation errors
                    s_val = float(start_p.iloc[0]) if isinstance(start_p, pd.Series) else float(start_p)
                    e_val = float(end_p.iloc[0]) if isinstance(end_p, pd.Series) else float(end_p)
                    
                    growth_pct = ((e_val - s_val) / s_val) * 100
                    results.append({
                        "Asset": sym, 
                        "Growth (%)": round(growth_pct, 2), 
                        "Price at Start": round(s_val, 2),
                        "Price at End": round(e_val, 2)
                    })

        if results:
            df = pd.DataFrame(results).sort_values(by="Growth (%)", ascending=False)
            top_asset = df.iloc[0]
            
            st.success(f"Best Performer: {top_asset['Asset']}")
            
            final_val = investment_amount * (1 + top_asset['Growth (%)']/100)
            st.metric(f"Your {investment_amount} would become:", f"{final_val:,.2f}", f"{top_asset['Growth (%)']}%")
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(df)
            with col2:
                best_data = yf.download(top_asset['Asset'], start=start_date, end=end_date)
                fig = go.Figure(data=[go.Scatter(x=best_data.index, y=best_data['Close'], mode='lines')])
                fig.update_layout(title=f"Price Trend: {top_asset['Asset']}")
                st.plotly_chart(fig)
        else:
            st.warning("No data found for this selection.")