
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas_datareader import get_data_yahoo as yh

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
periods = []
ending_return = []
subdata = df[['USDCAD','EURUSD','USDSGD','AUDUSD','NZDUSD','GBPUSD']] 
returns = subdata.pct_change()
subdata = subdata.shift() # remove data snooping

i=20
period = i
strongest_signal = subdata.pct_change(period).rolling(100).mean()

# account for different volatilities
target_volatility = 0.08
vola_scaler = (target_volatility/16) / returns.std()
strongest_signal = strongest_signal*vola_scaler

strongest_signal = strongest_signal.rank(axis=1, ascending = False)
# swap the numbers if you want momentum / mean reversion
strongest_signal[strongest_signal==1] = -1
strongest_signal[strongest_signal==len(strongest_signal.columns)] = 1
strongest_signal[(strongest_signal>1) & (strongest_signal<len(strongest_signal.columns))] = 0

strongest_signal = strongest_signal.dropna()

#scale returns by the target vola
target_daily_volatility = target_volatility / 16
returns_scaled = returns*vola_scaler

performance = (1+((strongest_signal*returns_scaled).sum(axis=1))).cumprod()
performance.plot(title = str(i) + ' Day Mean Reversion Smoothed')
plt.show()
periods.append(i)
ending_return.append(performance.tail(1).values[0])
print('Volatility Scaler')
print(vola_scaler)
print('\n')
print('Latest Signal')
print(strongest_signal.tail(1).T)

print('\n')
pret = (strongest_signal*returns_scaled).sum(axis=1)
print('Strategy Sharpe: ' + str((pret.mean() / pret.std())*16) )
print('Strategy Return ' + str(((1+pret.mean())**256)-1))
print('Strategy Volatility ' + str(pret.std()*16))

turnover = (strongest_signal != strongest_signal.shift())
print('\n' + 'Turnover:\n' + str(turnover.resample('Y').sum().sum(axis=1)))
