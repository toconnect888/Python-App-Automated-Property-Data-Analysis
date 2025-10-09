import pandas as pd
mydataset = {
    
  'cars': ["BMW", "Volvo", "Ford"],
  'passings': [3, 7, 2]
}

myvar = pd.DataFrame(mydataset,index = [1, 2, 3])

print(myvar)
print(myvar.iloc[0,0])


data = {
  "calories": [420, 380, 390],
  "duration": [50, 40, 45]
}
table = pd.DataFrame(data, index = ["day1", "day2", "day3"])

print(table)
print(table.loc["day1"])


# # colomn2 = pd.Series([1, 2, 3, 4, 5, 6]) 
# # print(colomn2)

# a = [1, 7, 2]

# myvar = pd.Series(a, index = ["x", "y", "z"])

# print(myvar)

building = pd.read_csv('buildinginfo.csv')
pd.options.display.max_rows = 9999  #change max rows (defalut 60 rows) to 9999 rows
print(pd.options.display.max_rows) # display max rows
print(building)
print(building.info()) # get information about the data in the csv file
print(building.head(10)) #read the first 10 rows of the data in the csv file
print(building.tail(10)) #read the last 10 rows of the data in the csv file



# duration=pd.read_json('duration.js')
# print(duration)