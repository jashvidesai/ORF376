from networkx import dfs_edges, dfs_labeled_edges
import pandas as pd
import numpy as np
import random

categories_info = {
    "Students leaving from an after-school program": {"size": 400, "age_range": (11, 18)},
}

weekdays = ["M", "Tu", "W", "Th", "F"]
weekend = ["Sa", "Su"]
all_days = weekdays + weekend

trip_types = {
    "Students leaving from an after-school program": ["School -> House"],
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
            
            if category == "Students leaving from an after-school program":
                for day in np.random.choice(weekdays, np.random.randint(1, 6), replace=False):
                    departure_time = random.choice(["15:30", "16:00", "16:30", "17:00", "17:30"])
                    rows.append([category, id_counter, gender, age, "School -> House", day, departure_time])

                id_counter += 1
    
    return pd.DataFrame(rows, columns=["Category", "ID", "Gender", "Age", "Trip Type", "Trip Departure Day", "Trip Departure Time"])

# generate and save the DataFrame
trip_data = generate_trip_data()
trip_data.to_excel("TransportationPeople_Group2.xlsx", index=False)


# Now we have the people file! Let's do the matching.


# Update the departure times
weekdays = ["M", "Tu", "W", "Th", "F"]
trip_data_school2 = trip_data[trip_data['Category'] == "Students leaving from an after-school program"].copy()

# add 'House Location' column to trip_data
unique_ids = trip_data['ID'].unique()
house_locations = {uid: random.choice(['EM', 'NM', 'WM', 'SM', 'CM']) for uid in unique_ids}
trip_data_school2['House Location'] = trip_data_school2['ID'].map(house_locations)

# Function for 'School Location' based on House Location and Age
def assign_school_location(house_location, age):
    if house_location in ['NM', 'WM']:
        if age <= 13:
            return 'Jefferson MS'
        else:
            return 'Dow HS'
    elif house_location in ['EM', 'SM']:
        if age <= 13:
            return 'Northeast MS'
        else:
            return 'Midland HS'
    else:
        if age <= 13:
            return random.choice(['Jefferson MS', 'Northeast MS'])
        else:
            return random.choice(['Dow HS', 'Midland HS'])

trip_data_school2['School Location'] = trip_data_school2.apply(lambda x: assign_school_location(x['House Location'], x['Age']), axis=1)

# function to assign group numbers (of size 4) based on departure times and locations
def assign_group_numbers(data):
    group_counter = 1

    # loop over each day and handles morning + afternoon trips separately
    for day in weekdays:
        # Afternoon trips: School -> House
        afternoon_data = data[(data['Trip Departure Day'] == day) & (data['Trip Type'] == "School -> House")]
        afternoon_data['Group Number'] = np.nan  # Initialize group numbers

        # Try to form groups based on all three criteria first
        for school in afternoon_data['School Location'].unique():
            for time in afternoon_data['Trip Departure Time'].unique():
                school_time_data = afternoon_data[
                    (afternoon_data['School Location'] == school) & 
                    (afternoon_data['Trip Departure Time'] == time)
                ]

                for i in range(0, len(school_time_data), 4):
                    if len(school_time_data.iloc[i:i+4]) < 4:
                        continue  # Skip if the group would be less than 4

                    data.loc[school_time_data.index[i:i+4], 'Group Number'] = f'{group_counter}'
                    group_counter += 1

        # Fill remaining spots in groups by relaxing the house location criteria
        remaining_data = afternoon_data[pd.isna(afternoon_data['Group Number'])]
        for school in remaining_data['School Location'].unique():
            for time in remaining_data['Trip Departure Time'].unique():
                remaining_school_time_data = remaining_data[
                    (remaining_data['School Location'] == school) & 
                    (remaining_data['Trip Departure Time'] == time)
                ]

                while len(remaining_school_time_data) > 0:
                    group_data = remaining_school_time_data.iloc[:4]  # Take up to 4
                    data.loc[group_data.index, 'Group Number'] = f'{group_counter}'
                    remaining_school_time_data = remaining_school_time_data.iloc[4:]
                    group_counter += 1

    return data

trip_data_school2 = assign_group_numbers(trip_data_school2)
trip_data_school2.to_excel("School2Groups.xlsx", index=False)

group_counts = trip_data_school2.groupby(['Trip Departure Day', 'Trip Type'])['Group Number'].nunique()
print(group_counts)