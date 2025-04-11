import requests
import yfinance as yf
import time
import telebot

# Telegram credentials
TOKEN = '7575897337:AAFPboSmtvE0t_EaGtgXPqwrzskQ1AEyIPg'
CHAT_ID = '7009947090'
bot = telebot.TeleBot(TOKEN)

# RapidAPI credentials
rapidapi_key = "39ff0c8b44mshdd462696a218ceap128169jsn9995aedfa583"
headers = {
    "x-rapidapi-host": "real-time-finance-data.p.rapidapi.com",
    "x-rapidapi-key": rapidapi_key
}

# Stocks list
stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]

def fetch_signal_and_price(symbol):
    try:
        data = yf.download(tickers=symbol, period='1d', interval='15m')
        if data.empty or len(data['Close']) < 2:
            return "Data unavailable", "N/A", "N/A", "N/A"

        latest_close = data['Close'].iloc[-1]
        previous_close = data['Close'].iloc[-2]

        latest_close = float(latest_close)
        previous_close = float(previous_close)

        if latest_close > previous_close:
            signal = "Buy"
            target = round(latest_close * 1.02, 2)  # +2%
            stoploss = round(latest_close * 0.98, 2)  # -2%
        elif latest_close < previous_close:
            signal = "Sell"
            target = round(latest_close * 0.98, 2)  # -2%
            stoploss = round(latest_close * 1.02, 2)  # +2%
        else:
            signal = "Hold"
            target = latest_close
            stoploss = latest_close

        return signal, latest_close, target, stoploss

    except Exception as e:
        return f"Error: {e}", "N/A", "N/A", "N/A"

def fetch_cash_flow(symbol):
    try:
        url = f"https://real-time-finance-data.p.rapidapi.com/company-cash-flow?symbol={symbol}&period=QUARTERLY&language=en"
        response = requests.get(url, headers=headers)
        data = response.json()

        cash_flow_data = data.get('data', {}).get('cashFlowStatements', [])
        if not cash_flow_data:
            return "Cash Flow Data Not Available"

        latest_cash_flow = cash_flow_data[0]
        operating_cash_flow = latest_cash_flow.get('operatingCashFlow', 'N/A')
        free_cash_flow = latest_cash_flow.get('freeCashFlow', 'N/A')

        return f"Operating Cash Flow: {operating_cash_flow}\nFree Cash Flow: {free_cash_flow}"
    except Exception as e:
        return f"Cash Flow Error: {e}"

def send_telegram_message(message):
    bot.send_message(CHAT_ID, message)

def main():
    while True:
        report = "📊 Market Update\n\n"
        for stock in stocks:
            # Convert symbol for API (RELIANCE.NS -> RELIANCE:NSE)
            api_symbol = stock.replace(".NS", ":NSE")

            signal, price, target, stoploss = fetch_signal_and_price(stock)
            cash_flow = fetch_cash_flow(api_symbol)

            report += (
                f"🔹 {stock.replace('.NS', '')} Update:\n"
                f"Signal: {signal}\n"
                f"Price: ₹{price}\n"
                f"Target: ₹{target}\n"
                f"Stoploss: ₹{stoploss}\n"
                f"{cash_flow}\n\n"
            )

        report += "⏱ Next update in: 5 min"
        send_telegram_message(report)

        time.sleep(300)  # Sleep for 5 minutes

if __name__ == "__main__":
    main()
