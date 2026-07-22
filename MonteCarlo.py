import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import sys

#From here we have to set parameters for the variables of Starting price, Drift, Total time horizon in years (This is just how far ahead you would like your simulation to go)
#volatility and the number of paths you would like - we could yahoo finance for this

ticker = input("Input the ticker you want to track: ") #User will input the ticker they want to track here e.g. "AAPL" or "MSFT"
stock = yf.Ticker(ticker)

suffixes = ("d", "mo", "y", "D","MO","Y", "Mo", "mO") #Stores Suffixes
time = input("How much historical data do you want? (input it as the number followed by d, mo or y for day, month and year respectively): ") #Ensures the suffixes are valid 
if not time.endswith(suffixes):
    sys.exit("Invalid timeframe") #If not valid, code exists and user must retsart and input a proper suffix
    
if time.endswith("y"):
    n = int(time.strip("y"))
elif time.endswith("mo"):
    n = int(time.strip("mo"))/12
elif time.endswith("d"):
    n = int(time.strip("d"))/365
else:
    sys.exit("Not a valid timeframe")

time = time.lower()

#Everything to find the drift
rf = yf.Ticker("^TNX").history(period="1d")["Close"].iloc[-1] / 100 #Risk Free Rate
beta = stock.info["beta"] #Gets beta
rm = (stock.history(period=time)["Close"].iloc[-1]/stock.history(period=time)["Close"].iloc[0]) ** (1/n)-1 # Find expected market return

drift = rf + beta * (rm - rf) #Calculate drift from CAPM

n_paths = input("How many paths would you like to simulate?: ")



T = input("What is your desired time horizon?: ")

    
df = stock.history(period="1d") # Get the price from the previous days close
starting_price = df["Close"].iloc[-1] 
dt = int(T) / (int(T)*252) #caluculate Δt
n_steps = int(T)*252

# to get volatility I need to get the daily log return for each day(rₜ = ln(Pₜ / Pₜ₋₁)), then get daily volatility (σ_daily = √[ Σ(rₜ − r̄)² / (n − 1) ]), and then annualize it(σ_annual = σ_daily × √252)

"""
r1 = stock.history(period=time)["Close"].reset_index(drop=True) <<< This is the value for Pₜ in daily log return
r2 = stock.history(period=time)["Close"].reset_index(drop=True) <<< This is the value for Pₜ₋₁ daily log return

r3 =np.log((r1/r2)) <<< this is the vlaue of dialy log return
r - np.std(r3) <<< this is the daily volatility
rt = r * np.sqrt(252) <<< this is the annualized volatility

^my working to get the final code
"""
annual_volatility = np.std(np.log(stock.history(period=time)["Close"].reset_index(drop=True)/stock.history(period=time)["Close"].reset_index(drop=True).shift(1))) * np.sqrt(252) #Everything above put together


z = np.random.randn(n_steps, int(n_paths))

GBM = np.exp(np.cumsum((drift-(0.5*(annual_volatility**2)))*dt + annual_volatility*np.sqrt(dt)*z, axis = 0)) * starting_price

plt.plot(GBM, color = "#1a3d4f", alpha = 0.5, linewidth = 0.5)
plt.plot(np.mean(GBM, axis=1), color = "#bf1b2b")  # average movement of the stock


