import random
import pandas as pd
import numpy as np

categories_info = {
    "Family in Poverty Member": {"size": 1679, "age_range": (22, 62)}
}

weekdays = ["M", "Tu", "W", "Th", "F"]
weekend = ["Sa", "Su"]
all_days = weekdays + weekend

trip_types = {
    "Family in Poverty Member": ["House -> Work", "Work -> House", "House -> Store", "Store -> House", 
                                 "House -> Doctor", "Doctor -> House", "House -> Other", "Other -> House"]
}

poverty_trip_distribution = {"House -> Work": 0.5, "House -> Store": 0.3, "House -> Doctor": 0.1, "House -> Other": 0.1}

def standardize_time(time_str):
    if 'am' in time_str or 'pm' in time_str:
        time_str = time_str.strip().lower().replace(' am', '').replace(' pm', '')
        hour, minute = map(int, time_str.split(':'))
        if 'pm' in time_str and hour < 12:
            hour += 12
        elif 'am' in time_str and hour == 12:
            hour = 0
    else:
        hour, minute = map(int, time_str.split(':'))
    return f"{hour:02}:{minute:02}"

def random_time(start_hour, end_hour, min_hour=None):
    if min_hour is not None:
        start_hour = max(start_hour, min_hour + 1)
    if start_hour >= end_hour:
        return standardize_time(f"{end_hour:02}:{np.random.choice(['00', '15', '30', '45'])}")
    hour = np.random.randint(start_hour, end_hour + 1)
    minute = np.random.choice(["00", "15", "30", "45"])
    return standardize_time(f"{hour:02}:{minute}")

def calculate_return_time(initial_time):
    initial_hour, initial_minute = map(int, initial_time.split(":"))
    return_hour = initial_hour + 1
    return_minute = initial_minute + 30
    if return_minute >= 60:
        return_hour += 1
        return_minute -= 60
    return standardize_time(f"{return_hour % 24:02}:{return_minute:02}")

def generate_trip_data():
    rows = []
    id_counter = 1
    for category, info in categories_info.items():
        for i in range(info["size"]):
            age = np.random.randint(*info["age_range"])
            gender = np.random.choice(["M", "F"])
            trip_type_mapping = {
                "House -> Work": "Work -> House",
                "House -> Store": "Store -> House",
                "House -> Doctor": "Doctor -> House",
                "House -> Other": "Other -> House"
            }
            
            if i < (info["size"] // 2):
                for day in weekdays:
                    morning_departure_time = standardize_time(np.random.choice(["5:45 am", "6:00 am", "6:15 am", "6:30 am"], p=[0.25, 0.25, 0.25, 0.25]))
                    evening_departure_hour = np.random.randint(18, 26)  # from 6:00 pm to 2:00 am
                    evening_departure_time = standardize_time(f"{evening_departure_hour % 24:02}:{np.random.choice(['00', '15', '30', '45'])}")
                    rows.append([category, id_counter, gender, age, "House -> Work", day, morning_departure_time])
                    rows.append([category, id_counter, gender, age, "Work -> House", day, evening_departure_time])
            else:
                days = np.random.choice(all_days, np.random.randint(1, 8), replace=False)
                for day in days:
                    for trip_type in trip_types[category]:
                        initial_departure_time = random_time(8, 22)
                        return_trip_type = trip_type_mapping.get(trip_type, trip_type)
                        return_departure_time = calculate_return_time(initial_departure_time) if trip_type in ["House -> Store", "House -> Doctor"] else random_time(int(initial_departure_time.split(":")[0]) + 1, 22)
                        rows.append([category, id_counter, gender, age, trip_type, day, initial_departure_time])
                        rows.append([category, id_counter, gender, age, return_trip_type, day, return_departure_time])

            id_counter += 1
    
    return pd.DataFrame(rows, columns=["Category", "ID", "Gender", "Age", "Trip Type", "Trip Departure Day", "Trip Departure Time"])

# Generate and save the DataFrame
trip_data = generate_trip_data()
trip_data.to_excel("TransportationPeople_Group4.xlsx", index=False)

# Now we have the people file! Let's do the matching.
# We need to separate the people commuting to work/house and house/work from the rest of the trips
# The Work/House code will be similar to the schools ones, the others will be similar to Group 3 Code.

weekdays = ["M", "Tu", "W", "Th", "F"]
weekends = ["Sat", "Sun"]
trip_data_group4 = trip_data[trip_data['Category'] == "Family in Poverty Member"].copy()

# add 'House Location' column to trip_data
unique_ids = trip_data['ID'].unique()
house_locations = {uid: random.choice(['EM', 'NM', 'WM', 'SM', 'CM']) for uid in unique_ids}
trip_data_group4['House Location'] = trip_data_group4['ID'].map(house_locations)

# Function for 'Destination Location'
def assign_destination_location(triptype):
    if triptype in ['House -> Work', 'Work -> House']:
        return random.choice(['Dow Chemical Plant', 'Midland Wastewater Treatment Center'])
    elif triptype in ['House -> Store', 'Store -> House']:
        return random.choice(['Walmart', 'Meijer', 'Kroger', 'Target'])
    elif triptype in ['House -> Doctor', 'Doctor -> House']:
        return random.choice(['MidMichigan Health', 'Dow Family Health'])
    elif triptype in ['House -> Other', 'Other -> House']:
        return random.choice(['Random Node in WM', 'Random Node in EM', 'Random Node in NM', 'Random Node in SM', 'Random Node in CM'])

trip_data_group4['Destination Location'] = trip_data_group4.apply(lambda x: assign_destination_location(x['Trip Type']), axis=1)

# handle the work case separately
# group those in Walmart, Meijer, Target together. group those in Kroger, MidMichigan Health, Dow Family Health together.
# function to assign group numbers (of size 4) based on departure times and locations

# does store, doctor, and other trips first
def time_within_threshold(time1, time2, threshold=30):
    t1 = pd.to_datetime(time1, format='%H:%M')
    t2 = pd.to_datetime(time2, format='%H:%M')
    return abs((t2 - t1).total_seconds()) / 60 <= threshold

def assign_group_numbers_other(data, max_group_size=4):
    group_counter = 1

    # Define sets of destinations for grouping
    set_one_destinations = ['Walmart', 'Meijer', 'Target']
    set_two_destinations = ['MidMichigan Health', 'Dow Family Health', 'Kroger']
    random_nodes = ['Random Node in WM', 'Random Node in EM', 'Random Node in NM', 'Random Node in SM', 'Random Node in CM']

    # Loop over each day
    for day in data['Trip Departure Day'].unique():
        day_data = data[data['Trip Departure Day'] == day]

        # Group by trip direction (outgoing or returning)
        for direction in ['outgoing', 'returning']:
            if direction == 'outgoing':
                direction_data = day_data[day_data['Trip Type'].str.contains('House ->')]
            else:
                direction_data = day_data[day_data['Trip Type'].str.contains('-> House')]

            # Handle each destination group
            for destinations in [set_one_destinations, set_two_destinations, random_nodes]:
                group_data = direction_data[direction_data['Destination Location'].isin(destinations)]

                # Further group by destination and departure time proximity
                for destination in destinations:
                    destination_data = group_data[group_data['Destination Location'] == destination]
                    sorted_data = destination_data.sort_values(by='Trip Departure Time')

                    while not sorted_data.empty:
                        base_time = sorted_data.iloc[0]['Trip Departure Time']
                        base_location = sorted_data.iloc[0]['House Location']
                        base_destination = sorted_data.iloc[0]['Destination Location']

                        # Determine the grouping condition based on destination
                        if destination in random_nodes:
                            # Group by specific node for random trips
                            mask = sorted_data.apply(lambda row: time_within_threshold(row['Trip Departure Time'], base_time) and 
                                                     row['Destination Location'] == base_destination and
                                                     row['House Location'] == base_location, axis=1)
                        else:
                            # Group by time and location
                            mask = sorted_data.apply(lambda row: time_within_threshold(row['Trip Departure Time'], base_time) and 
                                                     row['House Location'] == base_location, axis=1)
                            
                        if mask.sum() < max_group_size:
                            # Relax the house location constraint if necessary
                            mask = sorted_data.apply(lambda row: time_within_threshold(row['Trip Departure Time'], base_time), axis=1)

                        # Form a group with up to max_group_size members
                        group_indices = sorted_data[mask].index[:max_group_size]
                        data.loc[group_indices, 'Group Number'] = f'{group_counter}'
                        sorted_data = sorted_data.drop(group_indices)
                        group_counter += 1

    return data

# Applying the function to the DataFrame
if trip_data_group4['Trip Type'].isin(['House -> Store', 'Store -> House', 'House -> Doctor', 'Doctor -> House', 'House -> Other', 'Other -> House']).any():
    # trip_data_group4['Group Number'] = np.nan
    trip_data_group4 = assign_group_numbers_other(trip_data_group4)

# now, let's handle the house to work and work to house trips
# function to assign group numbers (of size 4) based on departure times and locations
def assign_group_numbers_work(data):
    group_counter = 1

    # loop over each day and handles morning + afternoon trips separately
    for day in weekdays:
        # Process morning trips
        morning_data = data[(data['Trip Departure Day'] == day) & (data['Trip Type'] == "House -> Work")]
        morning_data['Group Number'] = np.nan  # Initialize group numbers
        
        for house in morning_data['House Location'].unique():
            for time in morning_data['Trip Departure Time'].unique():
                house_time_data = morning_data[(morning_data['House Location'] == house) & 
                                               (morning_data['Trip Departure Time'] == time)]
                # First, try to match all three criteria
                for work in house_time_data['Destination Location'].unique():
                    full_criteria_data = house_time_data[house_time_data['Destination Location'] == work]
                    for i in range(0, len(full_criteria_data), 4):
                        if len(full_criteria_data.iloc[i:i+4]) < 4:  # Check if less than 4 remain
                            break  # Move to relaxing criteria if less than 4 students match

                        data.loc[full_criteria_data.index[i:i+4], 'Group Number'] = f'{group_counter}'
                        group_counter += 1

                # Relax the work location criteria if groups of 4 can't be formed
                remaining_data = house_time_data[pd.isna(house_time_data['Group Number'])]
                for i in range(0, len(remaining_data), 4):
                    group_data = remaining_data.iloc[i:i+4]
                    data.loc[group_data.index, 'Group Number'] = f'{group_counter}'
                    group_counter += 1

        # Afternoon trips: Work -> House
        afternoon_data = data[(data['Trip Departure Day'] == day) & (data['Trip Type'] == "Work -> House")]
        afternoon_data['Group Number'] = np.nan

        # Try to form groups based on all three criteria first
        for work in afternoon_data['Destination Location'].unique():
            for time in afternoon_data['Trip Departure Time'].unique():
                work_time_data = afternoon_data[
                    (afternoon_data['Destination Location'] == work) & 
                    (afternoon_data['Trip Departure Time'] == time)
                ]

                for i in range(0, len(work_time_data), 4):
                    if len(work_time_data.iloc[i:i+4]) < 4:
                        continue  # Skip if the group would be less than 4

                    data.loc[work_time_data.index[i:i+4], 'Group Number'] = f'{group_counter}'
                    group_counter += 1

        # Fill remaining spots in groups by relaxing the house location criteria
        remaining_data = afternoon_data[pd.isna(afternoon_data['Group Number'])]
        for work in remaining_data['Destination Location'].unique():
            for time in remaining_data['Trip Departure Time'].unique():
                remaining_work_time_data = remaining_data[
                    (remaining_data['Destination Location'] == work) & 
                    (remaining_data['Trip Departure Time'] == time)
                ]

                while len(remaining_work_time_data) > 0:
                    group_data = remaining_work_time_data.iloc[:4]  # Take up to 4
                    data.loc[group_data.index, 'Group Number'] = f'{group_counter}'
                    remaining_work_time_data = remaining_work_time_data.iloc[4:]
                    group_counter += 1

    return data

if trip_data_group4['Trip Type'].isin(['House -> Work', 'Work -> House']).any():
    # trip_data_group4['Group Number'] = np.nan
    trip_data_group4 = assign_group_numbers_work(trip_data_group4)

# Save the updated DataFrame with group numbers
trip_data_group4.to_excel("PovertyGroups.xlsx", index=False)

# Print out the unique group counts by trip type and day
group_counts = trip_data_group4.groupby(['Trip Departure Day', 'Trip Type'])['Group Number'].nunique()
print(group_counts)