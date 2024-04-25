import pandas as pd
import numpy as np
import random

categories_info = {
    "Students to/from school": {"size": 264, "age_range": (14, 18)},
}

weekdays = ["M", "Tu", "W", "Th", "F"]
weekend = ["Sa", "Su"]
all_days = weekdays + weekend

trip_types = {
    "Students to/from school": ["House -> School", "School -> House"],
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
            
            if category == "Students to/from school":
                for day in weekdays:
                    for trip_type in trip_types[category]:
                        if trip_type == "House -> School":
                            departure_time = random.choice(["6:30", "6:45", "7:00"])
                        else:
                            departure_time = random.choice(["14:45", "15:00", "15:15"])
                        rows.append([category, id_counter, gender, age, trip_type, day, departure_time])
                id_counter += 1
    
    return pd.DataFrame(rows, columns=["Category", "ID", "Gender", "Age", "Trip Type", "Trip Departure Day", "Trip Departure Time"])

# generate and save the DataFrame
trip_data = generate_trip_data()
trip_data.to_excel("TransportationPeople_Group1.xlsx", index=False)

# Now we have the people file! Let's do the matching.

# Update the departure times
trip_data.loc[trip_data['Trip Departure Time'] == '07:15', 'Trip Departure Time'] = '06:30'

weekdays = ["M", "Tu", "W", "Th", "F"]
trip_data_school1 = trip_data[trip_data['Category'] == "Students to/from school"].copy()

# add 'House Location' and 'School Location' columns to trip_data
unique_ids = trip_data['ID'].unique()
house_locations = {uid: random.choice(['EM', 'NM', 'WM', 'SM', 'CM']) for uid in unique_ids}
trip_data_school1['House Location'] = trip_data_school1['ID'].map(house_locations)

def assign_school_location(house_location):
    if house_location in ['NM', 'WM']:
        return 'Dow'
    elif house_location in ['EM', 'SM']:
        return 'Midland'
    else:  # 'CM'
        return random.choice(['Dow', 'Midland'])

school_locations = {uid: assign_school_location(house) for uid, house in house_locations.items()}
trip_data_school1['School Location'] = trip_data_school1['ID'].map(school_locations)

# function to assign group numbers (of size 4) based on departure times and locations
def assign_group_numbers(data):
    group_counter = 1

    # loop over each day and handles morning + afternoon trips separately
    for day in weekdays:
        # Process morning trips
        morning_data = data[(data['Trip Departure Day'] == day) & (data['Trip Type'] == "House -> School")]
        morning_data['Group Number'] = np.nan  # Initialize group numbers
        
        for house in morning_data['House Location'].unique():
            for time in morning_data['Trip Departure Time'].unique():
                house_time_data = morning_data[(morning_data['House Location'] == house) & 
                                               (morning_data['Trip Departure Time'] == time)]
                # First, try to match all three criteria
                for school in house_time_data['School Location'].unique():
                    full_criteria_data = house_time_data[house_time_data['School Location'] == school]
                    for i in range(0, len(full_criteria_data), 4):
                        if len(full_criteria_data.iloc[i:i+4]) < 4:  # Check if less than 4 remain
                            break  # Move to relaxing criteria if less than 4 students match

                        data.loc[full_criteria_data.index[i:i+4], 'Group Number'] = f'{group_counter}'
                        group_counter += 1

                # Relax the school location criteria if groups of 4 can't be formed
                remaining_data = house_time_data[pd.isna(house_time_data['Group Number'])]
                for i in range(0, len(remaining_data), 4):
                    group_data = remaining_data.iloc[i:i+4]
                    data.loc[group_data.index, 'Group Number'] = f'{group_counter}'
                    group_counter += 1

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

trip_data_school1 = assign_group_numbers(trip_data_school1)
trip_data_school1.to_excel("School1Groups.xlsx", index=False)

group_counts = trip_data_school1.groupby(['Trip Departure Day', 'Trip Type'])['Group Number'].nunique()
print(group_counts)