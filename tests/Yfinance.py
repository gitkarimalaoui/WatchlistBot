import yfinance as yf
df = yf.download("SPCE", period="5d", interval="1d")
print(df)
