# TSLA Trading Analysis App

This Streamlit application provides a comprehensive analysis of TSLA stock data with interactive candlestick charts and AI-powered analysis using Google's Gemini API.

## Features

- Interactive candlestick chart with support and resistance bands
- Direction markers (green up arrows for LONG, red down arrows for SHORT, yellow circles for None)
- Animated playback of price movements
- AI-powered analysis using Google's Gemini API
- Real-time chat interface for asking questions about the data

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Usage

### Trading Chart Tab
- View the candlestick chart with support and resistance bands
- Click "Start Animation" to see the price movements over time
- Green bands indicate support levels
- Red bands indicate resistance levels
- Direction markers show trading signals:
  - Green up arrows: LONG positions
  - Red down arrows: SHORT positions
  - Yellow circles: No position

### AI Analysis Tab
- Ask questions about the TSLA data in natural language
- The AI will analyze the data and provide insights
- Chat history is maintained during the session

## Data Format

The application expects a CSV file named `TSLA_data.csv` with the following columns:
- timestamp: Date of the data point
- direction: Trading direction (LONG, SHORT, or empty)
- Support: List of support levels
- Resistance: List of resistance levels
- open: Opening price
- high: Highest price
- low: Lowest price
- close: Closing price
- volume: Trading volume 