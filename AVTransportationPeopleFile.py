import pandas as pd
import numpy as np
import random

categories_info = {
    "Students to/from school": {"size": 264, "age_range": (14, 18)},
    "Students leaving from an after-school program": {"size": 400, "age_range": (11, 18)},
    "Elderly": {"size": 674, "age_range": (65, 90)},
    "Family in Poverty Member": {"size": 1679, "age_range": (22, 62)}
}

weekdays = ["M", "Tu", "W", "Th", "F"]
weekend = ["Sa", "Su"]
all_days = weekdays + weekend

trip_types = {
    "Students to/from school": ["House -> School", "School -> House"],
    "Students leaving from an after-school program": ["School -> House"],
    "Elderly": ["House -> Store", "Store -> House", "House -> Doctor", "Doctor -> House", "House -> Other", "Other -> House"],
    "Family in Poverty Member": ["House -> Work", "Work -> House", "House -> Store", "Store -> House", "House -> Doctor", "Doctor -> House", "House -> Other", "Other -> House"]
}

elderly_trip_distribution = {"House -> Store": 0.4, "House -> Doctor": 0.2, "House -> Other": 0.4}
poverty_trip_distribution = {"House -> Work": 0.5, "House -> Store": 0.3, "House -> Doctor": 0.1, "House -> Other": 0.1}

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
            
            elif category == "Students leaving from an after-school program":
                for day in np.random.choice(weekdays, np.random.randint(1, 6), replace=False):
                    departure_time = random.choice(["15:30", "15:45", "16:00", "16:15", "16:30", "16:45", "17:00", "17:15", "17:30"])
                    rows.append([category, id_counter, gender, age, "School -> House", day, departure_time])

                id_counter += 1
            
            elif category == "Elderly":
                num_days = np.random.randint(0, 3)  # This will give you 0, 1, or 2
                selected_days = np.random.choice(weekend, num_days, replace=False)
                selected_trip_type = np.random.choice(list(elderly_trip_distribution.keys()), p=list(elderly_trip_distribution.values()))
                for day in selected_days:
                    # generate two trips for each selected day with logical departure times
                    initial_departure_time = random_time(6, 19)
                    if selected_trip_type in ["House -> Store", "House -> Doctor"]:
                        return_departure_time = calculate_return_time(initial_departure_time)
                    else:
                        return_departure_time = random_time(int(initial_departure_time.split(":")[0]) + 1, 20)
        
                    rows.append([category, id_counter, gender, age, selected_trip_type, day, initial_departure_time])
                    return_trip_type = selected_trip_type.replace("House", "Return").replace("->", "<-") if selected_trip_type in ["House -> Store", "House -> Doctor"] else selected_trip_type.replace("Return", "House").replace("<-", "->")
                    rows.append([category, id_counter, gender, age, return_trip_type, day, return_departure_time])
                
                id_counter += 1
         
            elif category == "Family in Poverty Member":
                trip_type_mapping = {
                    "House -> Work": "Work -> House",
                    "House -> Store": "Store -> House",
                    "House -> Doctor": "Doctor -> House",
                    "House -> Other": "Other -> House"
                }
                for _ in range(info["size"]):
                    gender = np.random.choice(["M", "F"])
                    age = np.random.randint(*info["age_range"])

                    if id_counter <= (info["size"] // 2):
                    # Employed, specific departure times for House -> Work and variable for Work -> House
                        for day in weekdays:
                            morning_departure_time = np.random.choice(["5:45 am", "6:00 am", "6:15 am", "6:30 am"], p=[0.25, 0.25, 0.25, 0.25])
                            evening_departure_hour = np.random.randint(18, 26)  # from 6:00 pm to 2:00 am
                            evening_departure_time = f"{evening_departure_hour % 24:02d}:{np.random.choice(['00', '15', '30', '45'])}"
                            rows.append([category, id_counter, gender, age, "House -> Work", day, morning_departure_time])
                            rows.append([category, id_counter, gender, age, "Work -> House", day, evening_departure_time])
                    else:
                    # Not employed, random trips with time from 8:00 am to 10:00 pm
                        days = np.random.choice(all_days, np.random.randint(1, 8), replace=False)
                        for day in days:
                            for trip_type in trip_types[category]:
                                initial_departure_time = random_time(8, 22)  # random time from 8:00 am to 10:00 pm
                                return_trip_type = trip_type_mapping.get(trip_type, trip_type)
                                return_departure_time = calculate_return_time(initial_departure_time) if trip_type in ["House -> Store", "House -> Doctor"] else random_time(int(initial_departure_time.split(":")[0]) + 1, 22)
                                rows.append([category, id_counter, gender, age, trip_type, day, initial_departure_time])
                                rows.append([category, id_counter, gender, age, return_trip_type, day, return_departure_time])
        
                    id_counter += 1  # Increment id_counter inside the outer for loop to ensure proper counting
    
    return pd.DataFrame(rows, columns=["Category", "ID", "Gender", "Age", "Trip Type", "Trip Departure Day", "Trip Departure Time"])

# generate and save the DataFrame
trip_data = generate_trip_data()
trip_data.to_excel("TransportationPeople.xlsx", index=False)