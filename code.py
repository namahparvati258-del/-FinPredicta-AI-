import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go

# Page Setup
st.set_page_config(page_title="FinPredicta AI", layout="wide")
st.title("📈 FinPredicta: AI-Powered Investment Advisor")
st.write("Analyze stocks, compare sectors, and see how much your money can grow!")

# --- SIDEBAR: Date Selection ---
st.sidebar.header("Step 1: Select Time Period")
today = datetime.date.today()
# Default to 1 year ago
start_date = st.sidebar.date_input("Start Date", today - datetime.timedelta(days=365))
end_date = st.sidebar.date_input("End Date", today)

# Sector List
sectors = {
    "Petroleum & Energy": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "XOM", "CVX"],
    "Banking & Finance": ["HDFCBANK.NS", "ICICIBANK.NS", "SBI.NS", "JPM", "BAC"],
    "IT & Technology": ["TCS.NS", "INFY.NS", "AAPL", "GOOGL", "MSFT", "NVDA"],
    "Cryptocurrency": ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD"],
    "Automobile": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "F", "TM"]
}

# --- MAIN SECTION ---
st.subheader("Step 2: Choose What to Analyze")
search_mode = st.radio("What would you like to do?", ["Compare a Whole Sector", "Search for a Specific Company"])

if search_mode == "Search for a Specific Company":
    ticker_symbol = st.text_input("Enter Company Symbol (Example: RELIANCE.NS, AAPL, or BTC-USD):", "RELIANCE.NS")
    search_list = [ticker_symbol.upper()]
else:
    selected_sector = st.selectbox("Select a Sector to compare stocks:", list(sectors.keys()))
    search_list = sectors[selected_sector]

st.subheader("Step 3: Investment Amount")
investment_amount = st.number_input("How much money do you want to invest? (₹/$):", min_value=1, value=1000)

if st.button("Start Analysis"):
    if start_date >= end_date:
        st.error("Error: The Start Date must be before the End Date. Please fix the dates in the sidebar.")
    else:
        results = []
        with st.spinner('Fetching latest market data... please wait.'):
            for sym in search_list:
                data = yf.download(sym, start=start_date, end=end_date)
                if not data.empty:
                    start_p = data['Close'].iloc[0]
                    end_p = data['Close'].iloc[-1]
                    growth_pct = ((end_p - start_p) / start_p) * 100
                    results.append({
                        "Company": sym, 
                        "Growth (%)": round(growth_pct, 2), 
                        "Price at Start": round(float(start_p), 2),
                        "Price at End": round(float(end_p), 2)
                    })

        if results:
            df = pd.DataFrame(results).sort_values(by="Growth (%)", ascending=False)
            top_asset = df.iloc[0]
            
            # --- Results Summary ---
            st.success(f"Done! Based on your dates, **{top_asset['Company']}** performed the best.")
            
            projected_val = investment_amount * (1 + top_asset['Growth (%)']/100)
            st.metric(f"Your {investment_amount} would have become:", f"{projected_val:,.2f}", f"{top_asset['Growth (%)']}% Growth")
            
            # --- Visuals ---
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("### Full Performance List")
                st.dataframe(df, use_container_width=True)
            
            with col2:
                # Plotting the journey of the best stock
                best_data = yf.download(top_asset['Company'], start=start_date, end=end_date)
                fig = go.Figure(data=[go.Scatter(x=best_data.index, y=best_data['Close'], mode='lines', name=top_asset['Company'])])
                fig.update_layout(title=f"Price History of {top_asset['Company']}", xaxis_title="Date", yaxis_title="Price")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Sorry, no data found. Please check if the symbol is correct or try different dates.")

st.markdown("---")
st.write("**Disclaimer:** This is an AI project for learning. Please do your own research before investing money.")