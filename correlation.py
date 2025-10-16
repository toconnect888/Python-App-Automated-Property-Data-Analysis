import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from numpy import random

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


# print(arr[1, 1:4])
# print(arr[0:2, 1:4]) #slice index 1 to index 4 (not included),
# print(arr.shape)

# arr = np.array([1, 2, 3, 4, 5])
# x = arr.copy()
# arr[0] = 42

# print(arr)
# print(x)

arr = np.array([1, 2, 3, 4], ndmin=5)
print('shape of array :',arr.shape)

arr = np.array([1, 2, 3, 4, 5, 6])
newarr = arr.reshape(2, 3) #(2D array with 2 x 3 elements)
print(newarr)

for x in np.nditer(newarr):  #print all elements in this newarr array
  print(x)

for idx, x in np.ndenumerate(newarr): # print position of the element and the value of the element
  print(idx, x)

for x in np.nditer(newarr[:, ::2]):   #: print values “all rows” ,  “ every second column”
  print(x)

  
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])

arr_row = np.hstack((arr1, arr2))  #stack on rows
arr_col = np.vstack((arr1, arr2))  # stack on colomms
arr_height = np.dstack((arr1, arr2)) #stack on depths

print(arr_row)
print(arr_col)
print(arr_height)

arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18]])
arr_split_row = np.array_split(arr, 3) # split along rows into three 2D arrays
arr_split_col = np.hsplit(arr, 3)  # split along coloums into three 2D arrays
print(newarr)

index_finder = np.where(arr == 4)
even_index_finder = np.where(arr%2 == 0)
odd_index_finder = np.where(arr%2 == 1)

randomnumber = random.randint(100, size=(3, 5))  # (3,5) table with any number from 0-100
randomfloat = random.rand(3, 5)   #(3,5) table with any float number from 0-1

print(randomnumber)
print(randomfloat)

x = random.choice([3, 5, 7, 9], size=(3, 5))
print(x)
x = random.choice([3, 5, 7, 9], p=[0.1, 0.3, 0.6, 0.0], size=(100))
random.shuffle(x)

print(random.permutation(arr))
sns.displot([0, 1, 2, 3, 4, 5], kind="kde")
plt.show()

sns.displot(random.normal(size=1000), kind="kde")
plt.show()


def myadd(x, y):
  return x+y
myadd = np.frompyfunc(myadd, 2, 1)
print(myadd([1, 2, 3, 4], [5, 6, 7, 8]))

arr1 = np.trunc([-3.1666, 13.6667])  # Round number
arr2 = np.fix([-8.1666, 13.6667])  #round number
arrsum = np.sum([arr1, arr2])         #add all values to one total number
addrow = np.sum([arr1, arr2], axis=1)  # add value of each row
addcol = np.sum([arr1,arr2], axis = 0)  #add value of each colomn
print(addcol)
print(np.cumsum(arr1))   #add cumulative sum

arr = np.arange(1, 10)  
print(np.log2(arr)) # calculate log 2 of each value in the array

print(np.prod(arr))  # multiple every value in the array
print(np.prod(arr, axis=0)) # multiply down each column 

print(np.diff(arr)) # subtracting two successive elements.
print(np.diff(arr, n=2))  # discrete difference of the array twice

print(np.lcm.reduce([3,6,9]))  # the first number values can fit into without leaving a remainder. = 18
print(np.gcd.reduce([3,6,9]))  #largest number that fits into all numbers evenly  = 3

print(np.unique(np.array([1, 1, 1, 2, 3, 4, 5, 5, 6, 7])))  #find unique number in the array
print(np.union1d(arr1, arr2))  #find unique value of arr1 and arr2
print(np.intersect1d(arr1, arr2, assume_unique=True)) #find same value in arr1 and arr2
print(np.setdiff1d(arr1, arr2, assume_unique=True))
print(np.setxor1d(arr1, arr2, assume_unique=True))  # find values that are NOT present in arr1 and arr2
