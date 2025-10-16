import pandas as pd

data = {
  'cars': ["BMW", "Volvo", "Ford"],
  "calories": [420, 380, 390],
  "duration": [50, 40, 45]
}
table = pd.DataFrame(data, index = ["day1", "day2", "day3"])
print(table)
print(table.loc["day1"])  #print all cars, calories and duration values of day 1
print(table.iloc[0,0])  #print first row first coloum value - BMW

myvar = pd.Series([1, 3, 8], index = ["x", "y", "z"])  #create one colomn with 1,3,8 with lable of x, y, z
print(myvar)

building = pd.read_csv('buildinginfo.csv') #read csv file
pd.options.display.max_rows = 9999  #change max rows (defalut 60 rows) to 9999 rows
print(pd.options.display.max_rows) # display max rows
print(building)
print(building.info()) # get information about the data in the csv file
print(building.head(10)) #read the first 10 rows of the data in the csv file
print(building.tail(10)) #read the last 10 rows of the data in the csv file

duration=pd.read_json('duration.js') #read json file
print(duration)