import pandas as pd

df = pd.read_excel('TripDetails_Group3.xlsx')
grouped = df.groupby('Group Number')['Travel Time (minutes)'].sum()
average_travel_time = grouped.sum() / len(grouped)

print("Average Trip Type for Group 3: ", average_travel_time)

df2 = pd.read_csv('TripDetails_Group4.csv')
grouped2 = df2.groupby('Group Number')['Travel Time (minutes)'].sum()
average_travel_time_2 = grouped2.sum() / len(grouped2)

print("Average Trip Time for Group 4: ", average_travel_time_2)