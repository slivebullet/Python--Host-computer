import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

time_list = np.arange(-1, 1, 0.1)
singal1 = 7 * np.sin(2 * np.pi * 200 * time_list)

plt.plot(time_list, singal1)
plt.show()

file_csv = pd.DataFrame({'x_time': time_list, 'y_amplitude': singal1})
file_csv.to_csv('SIN(X).csv')


# x_major_locator = MultipleLocator(2)
# y_major_locator = MultipleLocator(2)
# ax = plt.gca()
# ax.xaxis.set_major_locator(x_major_locator)
# ax.yaxis.set_major_locator(y_major_locator)

