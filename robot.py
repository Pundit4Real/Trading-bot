import MetaTrader5 as mt5
import pandas as pd
import numpy as np

def connect_to_mt5():
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        return False
    
    # Specify your account login details here
    account = 5395836  # Replace with your account number
    password = "pundit@2035P#"  # Replace with your account password
    server = "Deriv-Demo"  # Replace with your broker's server
    
    # Login to your account
    authorized = mt5.login(account, password=password, server=server)
    if not authorized:
        print("Failed to login to account, error code =", mt5.last_error())
        mt5.shutdown()
        return False
    
    print("Connected to MetaTrader 5")
    return True


def fetch_historical_data(symbol, timeframe, start_time, end_time):
    rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
    if rates is None:
        print("Failed to fetch historical data")
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

def identify_support_resistance(df):
    # Example: Use peak and valley detection algorithm for support and resistance levels
    smooth_close = df['close'].rolling(window=30).mean()  # Smoothing close prices
    peak_mask = (smooth_close == smooth_close.rolling(window=5, center=True).max())  # Peaks
    valley_mask = (smooth_close == smooth_close.rolling(window=5, center=True).min())  # Valleys
    support_levels = df[valley_mask]['low'].index
    resistance_levels = df[peak_mask]['high'].index
    
    # Draw support and resistance levels on the chart
    draw_levels(support_levels, 0x00FF00)  # Green color
    draw_levels(resistance_levels, 0xFF0000)  # Red color
    
    return support_levels, resistance_levels

def draw_levels(levels, color):
    for level in levels:
        # Create a label to represent the support/resistance level
        mt5.comment(level, level, "S/R Level", color)



def identify_trendlines(df):
    # Example: Fit linear regression line to closing prices to identify trendlines
    x = np.arange(len(df))
    y = df['close'].values
    slope, intercept = np.polyfit(x, y, 1)  # Fit linear regression line
    trendline_points = [(df.index[0], intercept), (df.index[-1], intercept + slope * len(df))]
    return trendline_points

def identify_chart_patterns(df):
    # Example: Look for triangle patterns based on trendline intersections
    # Note: This is a simplified example. Real implementation may be more complex.
    high_points = df[df['high'] == df['high'].rolling(window=3).max()]['high'].index
    low_points = df[df['low'] == df['low'].rolling(window=3).min()]['low'].index
    triangle_points = []
    for high in high_points:
        for low in low_points:
            if low < high:
                triangle_points.append((low, high))
    return triangle_points

def identify_candlestick_patterns(df):
    # Example: Look for bullish engulfing patterns
    bullish_engulfing = df[(df['close'] > df['open']) & (df['open'] < df['close'].shift(1)) & (df['close'] > df['open'].shift(1))]
    return bullish_engulfing.index

def decision_making(df, support_levels, resistance_levels, trendline_points, triangle_points, candlestick_patterns):
    # Example: Buy when price breaks above resistance, sell when price breaks below support
    decisions = []
    for idx, row in df.iterrows():
        if idx in candlestick_patterns:
            decisions.append("Buy Signal: Bullish Engulfing at {}".format(idx))
        elif idx in resistance_levels:
            decisions.append("Sell Signal: Price Breaks Above Resistance at {}".format(idx))
        elif idx in support_levels:
            decisions.append("Buy Signal: Price Breaks Below Support at {}".format(idx))
        else:
            decisions.append("No Signal")
    return decisions

# Main
if __name__ == "__main__":
    if connect_to_mt5():
        symbol = "EURUSD"
        timeframe = mt5.TIMEFRAME_M1
        start_time = pd.Timestamp("2023-01-01")
        end_time = pd.Timestamp("2024-05-01")
        df = fetch_historical_data(symbol, timeframe, start_time, end_time)
        if df is not None:
            support_levels, resistance_levels = identify_support_resistance(df)
            trendline_points = identify_trendlines(df)
            triangle_points = identify_chart_patterns(df)
            candlestick_patterns = identify_candlestick_patterns(df)
            decisions = decision_making(df, support_levels, resistance_levels, trendline_points, triangle_points, candlestick_patterns)
            for decision in decisions:
                print(decision)
        mt5.shutdown()
