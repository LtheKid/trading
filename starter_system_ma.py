
import pandas as pd
from pandas_datareader import get_data_yahoo as yh
import matplotlib.pyplot as plt

# df = yh(['AUDUSD=X',
#          'EURUSD=X',
#          'GBPUSD=X',
#          'USDCAD=X',
#          'USDSGD=X',
#          'NZDUSD=X',
#          'GLD',
#          'SPY',
#          'TLT',
#          'VT',
#          'BNDW',
#          'IAU',
#         'QQQ'])['Close']

# df.to_csv('data.csv')


df = pd.read_csv('data.csv', parse_dates = True, index_col='Date')
df.columns = df.columns.str.replace('=X','')
df = df[[
         'EURUSD',
         'GBPUSD',
         'USDCAD',
         'USDSGD',
         'NZDUSD',
         'SPY',
         'TLT',
         'VT',
         'BNDW',
         'IAU']]


df = df.dropna()
# df = df[['AUDUSD','USDCAD','USDSGD']]
prev = df.shift(1)
returns = df.pct_change()
returns = returns.dropna()
# notional exposure
# notional exposure = (target risk % x capital) / instrument risk %
pd.set_option('float_format','{:f}'.format)
exposure = pd.DataFrame(0.12*750 / (returns.std()*16))
exposure.columns = ['notional_exposure']

period_short = 21 #16
period_long = 50 #64

ma_short = prev.rolling(period_short).mean()
ma_long = prev.rolling(period_long).mean()
long = ma_short>ma_long
short = ma_short<ma_long
short.replace([1,0],[-1,0], inplace=True)
long.replace([1,0],[1,0], inplace=True)

# Target vola
def get_vola_scaler(returns, target_annualized_vola):
    return (target_annualized_vola/16) / returns.std()
    
returns_scaled = returns*get_vola_scaler(returns, 0.12)  

positions =short+long

# stop loss in price with 0.5 factor
sl_pips = (returns.std()*16) * 0.5 * df.tail(1)

stoploss = (df.tail(1) - sl_pips*positions).tail(1).T
stoploss.columns= ['stoploss']

last_price = df.tail(1).T
last_price.columns = ['close']

last_position = positions.tail(1).T
last_position.columns = ['position']

print(pd.concat([last_position,exposure,last_price, stoploss], axis=1))
(1+((positions*returns_scaled)).mean(axis = 1)).cumprod().plot()
plt.show()
