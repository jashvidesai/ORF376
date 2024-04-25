import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# find the average miles by each AV (across all groups)
df1 = pd.read_excel('TripDetails_Group1.xlsx', header=None)
df1[3] = pd.to_numeric(df1[3], errors='coerce')
df1 = df1.dropna(subset=[3])
group1_data = df1.groupby(0)[3].sum()
average_distance_1 = (group1_data.sum() / 74)/ 1609 # in miles

df2 = pd.read_excel('TripDetails_Group2.xlsx', header=None)
df2[3] = pd.to_numeric(df2[3], errors='coerce')
df2 = df2.dropna(subset=[3])
group2_data = df2.groupby(0)[3].sum()
average_distance_2 = (group2_data.sum() / 74) / 1609 # in miles

df3 = pd.read_excel('TripDetails_Group3.xlsx', header=None)
df3[3] = pd.to_numeric(df3[3], errors='coerce')
df3 = df3.dropna(subset=[3])
group3_data = df3.groupby(0)[3].sum()
average_distance_3 = (group3_data.sum() / 74) / 1609 # in miles

df4 = pd.read_csv('TripDetails_Group4.csv')
df4['Distance (meters)'] = pd.to_numeric(df4['Distance (meters)'], errors='coerce')
df4 = df4.dropna(subset=['Distance (meters)'])
group4_data = df4.groupby('Group Number')['Distance (meters)'].sum()
average_distance_4 = (group4_data.sum() / 93) / 1609 # in miles

average_distance_weekly = ((average_distance_1 + average_distance_2 + average_distance_3 + average_distance_4) / 4)
average_distance_annually = average_distance_weekly * 52
print("Average AV distance (in miles) annually: ", average_distance_annually)

# Constants
years = 10
GHG_EMISSIONS_GASOLINE = 8.89
GHG_EMISSIONS_ELECTRICITY = 0.4  # kg CO2-equivalent per kWh
EV_KWH_PER_MILE = np.random.normal(0.325, 0.075, years) # range of (0.25, 0.40) but for variability
COMPUTER_POWER_CONSUMPTION = 0.84  # kWh per hour
OPERATING_HOURS_PER_DAY = (1 + 2 + 13 + 9 + 14)/5  # Average operating hours per day (group 4 split into 2)

annual_miles_driven = np.random.normal(average_distance_annually, 2000, years)

# Fuel efficiency for gasoline vehicles (with variability)
MPG_GASOLINE = 26 # Constant average miles per gallon for gasoline vehicles
mpg_gasoline = np.random.normal(MPG_GASOLINE, 2, years)

# Electric vehicle energy consumption per mile (with variability)
kwh_per_mile = np.random.normal(EV_KWH_PER_MILE, 0.01, years)

# Function to calculate emissions
def calculate_emissions(miles, mpg, kwh_per_mile, hours_per_day):
    emissions_gasoline = miles / mpg * GHG_EMISSIONS_GASOLINE
    emissions_electric = miles * kwh_per_mile * GHG_EMISSIONS_ELECTRICITY
    emissions_computational = hours_per_day * COMPUTER_POWER_CONSUMPTION * GHG_EMISSIONS_ELECTRICITY * 365
    total_emissions_electric = emissions_electric + emissions_computational
    return emissions_gasoline, total_emissions_electric

# Plotting the results
emissions_gasoline, total_emissions_electric = calculate_emissions(annual_miles_driven, mpg_gasoline, kwh_per_mile, OPERATING_HOURS_PER_DAY)

plt.figure(figsize=(10, 6))
plt.plot(emissions_gasoline, label='Gasoline Vehicle Emissions', color='red')
plt.plot(total_emissions_electric, label='Total Electric Vehicle Emissions (including computation)', color='blue')
plt.title('Comparison of GHG Emissions Over 10 Years')
plt.xlabel('Year')
plt.ylabel('GHG Emissions (kg CO2-equivalent)')
plt.legend()
plt.grid(True)
plt.show()