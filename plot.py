import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys 
data = pd.read_csv(sys.argv[1])
x = data['epochs']
avg = data['average']
max_ = data['maximum']
max_z = np.polyfit(x, max_, 1)
max_p = np.poly1d(max_z)
plt.plot(x, max_p(x), "r--")
z = np.polyfit(x, avg, 1)
p = np.poly1d(z)

plt.plot(x,p(x),"r--")
plt.plot(data['average'], label='avg')
plt.plot(data['maximum'], label='max')
plt.legend()
plt.grid()
plt.show()
