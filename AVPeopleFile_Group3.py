import pandas as pd
import numpy as np
import random

categories_info = {
    "Elderly": {"size": 674, "age_range": (65, 90)}
}

weekdays = ["M", "Tu", "W", "Th", "F"]
weekend = ["Sa", "Su"]
all_days = weekdays + weekend

trip_types = {
    "Elderly": ["House -> Store", "Store -> House", "House -> Doctor", "Doctor -> House", "House -> Other", "Other -> House"],
}

# Update the distribution to include all trip types
elderly_trip_distribution = {
    "House -> Store": 0.2,
    "House -> Doctor": 0.2,
    "House -> Other": 0.2,
    "Store -> House": 0.1, 
    "Doctor -> House": 0.1,
    "Other -> House": 0.1
}

def random_time(start_hour, end_hour, min_hour=None):
    if min_hour is not None:
        start_hour = max(start_hour, min_hour + 1)
    if start_hour >= end_hour:
        return f"{end_hour:02d}:{np.random.choice(['00', '15', '30', '45'])}"
    hour = np.random.randint(start_hour, end_hour + 1)
    minute = np.random.choice(["00", "15", "30", "45"])
    return f"{hour:02d}:{minute}"

def calculate_return_time(initial_time):
    initial_hour, initial_minute = map(int, initial_time.split(":"))
    return_hour = initial_hour + 1
    return_minute = initial_minute + 30
    if return_minute >= 60:
        return_hour += 1
        return_minute -= 60
    return f"{return_hour % 24:02d}:{return_minute:02d}"

def generate_trip_data():
    rows = []
    id_counter = 1
    for category, info in categories_info.items():
        for _ in range(info["size"]):
            age = np.random.randint(*info["age_range"])
            gender = np.random.choice(["M", "F"])

            # Generate trips for each individual
            if category == "Elderly":
                num_days = np.random.randint(1, 3)  # Adjust to ensure at least one day is chosen
                selected_days = np.random.choice(weekend, num_days, replace=False)
                trip_types_available = ["House -> Store", "House -> Doctor", "House -> Other"]
                for day in selected_days:
                    selected_trip_type = np.random.choice(trip_types_available)  # Choose randomly among initial trips
                    initial_departure_time = random_time(6, 19)
                    return_departure_time = calculate_return_time(initial_departure_time)

                    # Append initial trip
                    rows.append([category, id_counter, gender, age, selected_trip_type, day, initial_departure_time])
                    
                    # Properly label return trip based on initial trip type
                    if selected_trip_type == "House -> Store":
                        return_trip_type = "Store -> House"
                    elif selected_trip_type == "House -> Doctor":
                        return_trip_type = "Doctor -> House"
                    elif selected_trip_type == "House -> Other":
                        return_trip_type = "Other -> House"
                    
                    # Append return trip
                    rows.append([category, id_counter, gender, age, return_trip_type, day, return_departure_time])
                
                id_counter += 1
    
    return pd.DataFrame(rows, columns=["Category", "ID", "Gender", "Age", "Trip Type", "Trip Departure Day", "Trip Departure Time"])

# generate and save the DataFrame
trip_data = generate_trip_data()
trip_data.to_excel("TransportationPeople_Group3.xlsx", index=False)


# Now we have the people file! Let's do the matching.


# Update the departure times
weekends = ["Sat", "Sun"]
trip_data_group3 = trip_data[trip_data['Category'] == "Elderly"].copy()

# add 'House Location' column to trip_data
unique_ids = trip_data['ID'].unique()
house_locations = {uid: random.choice(['EM', 'NM', 'WM', 'SM', 'CM']) for uid in unique_ids}
trip_data_group3['House Location'] = trip_data_group3['ID'].map(house_locations)

# Function for 'Destination Location'
def assign_destination_location(triptype):
    if triptype in ['House -> Store', 'Store -> House']:
        return random.choice(['Walmart', 'Meijer', 'Kroger', 'Target'])
    elif triptype in ['House -> Doctor', 'Doctor -> House']:
        return random.choice(['MidMichigan Health', 'Dow Family Health'])
    elif triptype in ['House -> Other', 'Other -> House']:
        return random.choice(['Random Node in WM', 'Random Node in EM', 'Random Node in NM', 'Random Node in SM', 'Random Node in CM'])

trip_data_group3['Destination Location'] = trip_data_group3.apply(lambda x: assign_destination_location(x['Trip Type']), axis=1)

# group those in Walmart, Meijer, Target together. group those in Kroger, MidMichigan Health, Dow Family Health together.
# function to assign group numbers (of size 4) based on departure times and locations

def time_within_threshold(time1, time2, threshold=30):
    t1 = pd.to_datetime(time1, format='%H:%M')
    t2 = pd.to_datetime(time2, format='%H:%M')
    return abs((t2 - t1).total_seconds()) / 60 <= threshold

def assign_group_numbers(data, max_group_size=4):
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
trip_data_group3['Group Number'] = np.nan
trip_data_group3 = assign_group_numbers(trip_data_group3)

# Save the updated DataFrame with group numbers
trip_data_group3.to_excel("ElderlyGroups.xlsx", index=False)

# Print out the unique group counts by trip type and day
group_counts = trip_data_group3.groupby(['Trip Departure Day', 'Trip Type'])['Group Number'].nunique()
print(group_counts)