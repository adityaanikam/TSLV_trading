import streamlit as st
import pandas as pd
import ast
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from streamlit_lightweight_charts import renderLightweightCharts

# --- Load environment variables and Gemini API ---
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
else:
    model = None

st.set_page_config(page_title="TSLA Trading Analysis", layout="wide")

def parse_list_string(s):
    if pd.isna(s) or s == '[]':
        return []
    try:
        return ast.literal_eval(s)
    except Exception:
        return []

@st.cache_data
def load_data():
    filename = 'TSLA_data.csv'
    if not os.path.exists(filename):
        st.warning("TSLA_data.csv not found. Please upload the file below.")
        uploaded = st.file_uploader("Upload TSLA_data.csv", type=["csv"])
        if uploaded is not None:
            df = pd.read_csv(uploaded)
        else:
            st.stop()
    else:
        df = pd.read_csv(filename)
    df['Support'] = df['Support'].apply(parse_list_string)
    df['Resistance'] = df['Resistance'].apply(parse_list_string)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = load_data()

# --- Data validation ---
invalid_rows = []
for idx, row in df.iterrows():
    o, h, l, c = row['open'], row['high'], row['low'], row['close']
    if pd.isna(o) or pd.isna(h) or pd.isna(l) or pd.isna(c):
        invalid_rows.append((idx, 'NaN'))
        continue
    if not all(isinstance(x, (int, float)) for x in [o, h, l, c]):
        invalid_rows.append((idx, 'Non-numeric'))
        continue
    if not (h >= max(o, c) and l <= min(o, c)):
        invalid_rows.append((idx, f'High/Low logic error: O={o}, H={h}, L={l}, C={c}'))
if invalid_rows:
    st.warning(f"Invalid OHLC rows: {invalid_rows}")
else:
    st.info("All OHLC rows valid.")

tab1, tab2 = st.tabs(["Trading Chart", "AI Analysis"])

with tab1:
    st.title("TSLA Trading Analysis")

    # --- Prepare candlestick data ---
    candles = [
        {
            "time": row['timestamp'].strftime('%Y-%m-%dT%H:%M:%S'),
            "open": row['open'],
            "high": row['high'],
            "low": row['low'],
            "close": row['close']
        }
        for _, row in df.iterrows()
    ]

    # --- Prepare markers ---
    markers = []
    for idx, row in df.iterrows():
        t = row['timestamp'].strftime('%Y-%m-%dT%H:%M:%S')
        if row['direction'] == 'LONG':
            markers.append({
                "time": t,
                "position": "belowBar",
                "color": "green",
                "shape": "arrowUp",
                "text": "LONG"
            })
        elif row['direction'] == 'SHORT':
            markers.append({
                "time": t,
                "position": "aboveBar",
                "color": "red",
                "shape": "arrowDown",
                "text": "SHORT"
            })
        else:
            markers.append({
                "time": t,
                "position": "inBar",
                "color": "yellow",
                "shape": "circle",
                "text": "None"
            })

    # --- Prepare support/resistance bands as area series ---
    support_area = []
    resistance_area = []
    for _, row in df.iterrows():
        t = row['timestamp'].strftime('%Y-%m-%dT%H:%M:%S')
        if row['Support']:
            support_area.append({
                "time": t,
                "value": min(row['Support']),
                "value2": max(row['Support'])
            })
        if row['Resistance']:
            resistance_area.append({
                "time": t,
                "value": min(row['Resistance']),
                "value2": max(row['Resistance'])
            })

    # --- Chart config ---
    chart_dict = {
        "width": 900,
        "height": 500,
        "layout": {"background": {"type": "solid", "color": "#18181b"}, "textColor": "#fff"},
        "grid": {"vertLines": {"color": "#444"}, "horzLines": {"color": "#444"}},
        "rightPriceScale": {"borderColor": "#71649C"},
        "timeScale": {"borderColor": "#71649C"},
        "crosshair": {"mode": 0},
        "series": [
            {
                "type": "Candlestick",
                "data": candles,
                "markers": markers,
                "upColor": "#26a69a",
                "downColor": "#ef5350",
                "borderVisible": True,
                "wickUpColor": "#26a69a",
                "wickDownColor": "#ef5350"
            },
            {
                "type": "Area",
                "data": support_area,
                "topColor": "rgba(0,255,0,0.2)",
                "bottomColor": "rgba(0,255,0,0.2)",
                "lineColor": "rgba(0,255,0,0.7)",
                "lineWidth": 1,
                "valueField": "value2",
                "baseValueField": "value"
            },
            {
                "type": "Area",
                "data": resistance_area,
                "topColor": "rgba(255,0,0,0.2)",
                "bottomColor": "rgba(255,0,0,0.2)",
                "lineColor": "rgba(255,0,0,0.7)",
                "lineWidth": 1,
                "valueField": "value2",
                "baseValueField": "value"
            }
        ]
    }

    # --- Animation controls (BONUS) ---
    st.write("")
    play = st.button("Start Animation")
    if play:
        for i in range(10, len(candles)+1):
            chart_dict["series"][0]["data"] = candles[:i]
            chart_dict["series"][0]["markers"] = markers[:i]
            support_count = sum(1 for j in range(i) if df.iloc[j]['Support'])
            resistance_count = sum(1 for j in range(i) if df.iloc[j]['Resistance'])
            chart_dict["series"][1]["data"] = support_area[:support_count]
            chart_dict["series"][2]["data"] = resistance_area[:resistance_count]
            renderLightweightCharts([chart_dict], key=f"chart_anim_{i}")
            time.sleep(0.1)
    else:
        renderLightweightCharts([chart_dict], key="chart_full")

with tab2:
    st.title("AI Analysis of TSLA Data")
    st.markdown("**Sample questions:**")
    st.markdown("- How many days in 2023 was TSLA bullish?")
    st.markdown("- What was the highest resistance level recorded?")
    st.markdown("- What's the average support level?")
    st.markdown("- How many SHORT signals were there in total?")
    st.markdown("- What was the largest single day price movement?")
    st.markdown("- Show me the distribution of LONG vs SHORT signals over time")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Ask about TSLA data"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        # --- Enhanced data context ---
        context = {
            "date_range": f"{df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}",
            "price_range": f"{df['low'].min():.2f} to {df['high'].max():.2f}",
            "signals": {
                "LONG": (df['direction'] == 'LONG').sum(),
                "SHORT": (df['direction'] == 'SHORT').sum(),
                "NEUTRAL": ((df['direction'] != 'LONG') & (df['direction'] != 'SHORT')).sum()
            },
            "support_stats": {
                "average": df['Support'].apply(lambda x: sum(x)/len(x) if len(x) > 0 else 0).mean(),
                "max": df['Support'].apply(lambda x: max(x) if len(x) > 0 else 0).max(),
                "min": df['Support'].apply(lambda x: min(x) if len(x) > 0 else 0).min()
            },
            "resistance_stats": {
                "average": df['Resistance'].apply(lambda x: sum(x)/len(x) if len(x) > 0 else 0).mean(),
                "max": df['Resistance'].apply(lambda x: max(x) if len(x) > 0 else 0).max(),
                "min": df['Resistance'].apply(lambda x: min(x) if len(x) > 0 else 0).min()
            },
            "volume_stats": {
                "average": df['volume'].mean(),
                "max": df['volume'].max(),
                "min": df['volume'].min()
            },
            "sample_data": df.head(3).to_dict(orient='records')
        }
        full_context = f"""
        You are analyzing TSLA stock data with the following characteristics:

        Date Range: {context['date_range']}
        Price Range: ${context['price_range']}

        Trading Signals:
        - LONG: {context['signals']['LONG']} occurrences
        - SHORT: {context['signals']['SHORT']} occurrences
        - NEUTRAL: {context['signals']['NEUTRAL']} occurrences

        Support Levels:
        - Average: {context['support_stats']['average']:.2f}
        - Maximum: {context['support_stats']['max']:.2f}
        - Minimum: {context['support_stats']['min']:.2f}

        Resistance Levels:
        - Average: {context['resistance_stats']['average']:.2f}
        - Maximum: {context['resistance_stats']['max']:.2f}
        - Minimum: {context['resistance_stats']['min']:.2f}

        Volume Statistics:
        - Average: {context['volume_stats']['average']:.2f}
        - Maximum: {context['volume_stats']['max']:.2f}
        - Minimum: {context['volume_stats']['min']:.2f}

        User Question: {prompt}
        """
        if model:
            try:
                response = model.generate_content(full_context)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                with st.chat_message("assistant"):
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
        else:
            st.error("Gemini API key not found or not configured.")