import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from collections import namedtuple

flocking= pd.read_csv(sys.argv[1])
qlearning = pd.read_csv(sys.argv[2])

# max_p = np.poly1d(np.polyfit(flocking['epochs'],flocking['maxiumum'], 1))
# max_mean = sum(flocking['maximum']) / len(flocking['maximum'])

plot_of_max = plt.figure(figsize=(8,6))
# plot_of_max.plot(x, [max_mean]*len(x), "--",
        #  label='Mean of maximum lifetime with flocking')
# plt.plot(x, max_p(x), "r--")
# z = np.polyfit(x, avg, 1)
# p = np.poly1d(z)
max_histogram = flocking['maximum'] - qlearning['maximum']
plt.title('Wykres maksymalnego czasu życia')
plt.plot(flocking['epochs'], flocking['maximum'], label='Maksymalny czas życia z zachowaniem ławicy')
plt.plot(qlearning['epochs'],qlearning['maximum'], label='Maksymalny czas życia bez zachowania ławicy')
plt.bar(flocking['epochs'], max_histogram, width=0.9, label='Różnica pomiędzy wartościami krzywych')
plt.xlabel('Liczba epok [n]')
plt.ylabel('Liczba przeżytych klatek')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()


average_historgram = flocking['average'] - qlearning['average']
plt.figure(figsize=(8,6))
plt.title('Wykres średniego czasu życia')
plt.plot(flocking['epochs'], flocking['average'], label='Średnia z zachowaniem ławicy')
plt.plot(qlearning['epochs'], qlearning['average'], label='Średnia bez zachowania ławicy')
plt.bar(flocking['epochs'], average_historgram, width=0.9, label='Różnica pomiędzy wartościami krzywych')
plt.xlabel('Liczba epok [n]')
plt.ylabel('Liczba przeżytych klatek')
plt.legend()
plt.tight_layout()
plt.grid()
plt.show()
