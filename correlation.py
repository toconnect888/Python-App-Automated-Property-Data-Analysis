import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
data = pd.read_csv('correlation.csv')

for x in data.index: # cap the duration to 120, "Duration" column. If value higher than 120, set it to 120:
  if data.loc[x, "Duration"] > 120:
    data.loc[x, "Duration"] = 120

data = data.dropna() #remove rows with null values
print(data)
print(data.corr())

data.plot() #linre graph
plt.show()

data.plot(kind='scatter', x='Duration', y='Calories') #scatter graph
plt.show()

data["Duration"].plot(kind = 'hist') #histogram
plt.show()


arr = np.array([[1, 2, 3, 4, 5], [7 ,8 ,9 ,10 ,11]])
# print(arr)


print(arr) #number of dimensions
print(arr[0] + arr[1])
print(arr)
print('number of dimensions :', arr.ndim)
print('2nd element on 1st row: ', arr[0, 1]) 
print('Last element from 1st row: ', arr[0, -1])