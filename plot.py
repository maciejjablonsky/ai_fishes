import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv('time_stats.csv')
x = data['epoch']
avg = data['avg']
max_ = data['max']
max_z = np.polyfit(x, max_, 1)
max_p = np.poly1d(max_z)
plt.plot(x, max_p(x), "r--")
z = np.polyfit(x, avg, 1)
p = np.poly1d(z)

plt.plot(x,p(x),"r--")
plt.plot(data['avg'], label='avg')
plt.plot(data['max'], label='max')
plt.legend()
plt.grid()
plt.show()
