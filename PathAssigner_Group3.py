from datetime import timedelta
import itertools
import random
import networkx as nx
import pandas as pd

# Constants
AV_SPEED_MPH = 60
STOP_TIME_MINUTES = 2
TRIP_DELAY_PROBABILITY = 0.01
TRIP_DELAY_MINUTES = 5
METERS_PER_MILE = 1609.34

# Load graph data
G = nx.read_graphml('Midland_road_network3.graphml')
G = G.to_undirected()
# Ensure all edges have a length attribute
for u, v, data in G.edges(data=True):
    data['length'] = float(data.get('length', 1))

# Load individuals data
individuals_df = pd.read_excel('ElderlyGroupsUpdated.xlsx')
individuals_df['House Node'] = individuals_df['House Node'].astype(str)
individuals_df['Destination Node'] = individuals_df['Destination Node'].astype(str)
individuals_df['Trip Departure Time'] = pd.to_datetime(individuals_df['Trip Departure Time'], format='%H:%M')

# Functions for path calculation
def calculate_total_path_length(G, path):
    return sum(nx.shortest_path_length(G, source=path[i], target=path[i + 1], weight='length') for i in range(len(path) - 1))

def get_full_path(G, path):
    full_path = []
    for i in range(len(path) - 1):
        part_path = nx.shortest_path(G, source=path[i], target=path[i + 1], weight='length')
        full_path.extend(part_path[:-1])  # Avoid duplicating nodes
    full_path.append(path[-1])  # Add the last node
    return full_path

# Define the optimal path finding function
def find_optimal_paths(G, individuals_df):
    optimal_paths = {}
    for group_number, group_df in individuals_df.groupby('Group Number'):
        min_length = float('inf')
        optimal_order = None
        optimal_full_path = None
        for perm in itertools.permutations(group_df.index):
            trip_nodes = [node for idx in perm for node in (group_df.loc[idx, 'House Node'], group_df.loc[idx, 'Destination Node'])]
            length = calculate_total_path_length(G, trip_nodes)
            if length < min_length:
                min_length = length
                optimal_order = trip_nodes
                optimal_full_path = get_full_path(G, trip_nodes)
        if optimal_full_path is not None:
        # Store the optimal path details in the dictionary
            optimal_paths[group_number] = {
                'optimal_order': optimal_order,
                'total_distance': min_length,
                'full_path': get_full_path(G, optimal_order)
            }
    return optimal_paths

# Find the optimal paths for each group
optimal_paths = find_optimal_paths(G, individuals_df)

# Output the results for each group
#for group_number, info in optimal_paths.items():
    #print(f"Group {group_number}:")
    #print(f"  Optimal Node Order: {info['optimal_order']}")
    #print(f"  Optimal Full Path: {info['optimal_full_path']}")
    #print(f"  Total Distance: {info['total_distance']}")

# After outputting the optimal order, we now can aim to calculate the timings

# Function to calculate travel time in minutes given distance in miles
def calculate_travel_time(distance_meters, speed_mph=AV_SPEED_MPH):
    distance_miles = distance_meters / METERS_PER_MILE
    travel_time_minutes = (distance_miles / speed_mph) * 60
    return travel_time_minutes

def process_trips(G, optimal_paths, individuals_df, delay_nodes, delay_time):
    node_coords = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
    delay_nodes_set = set(delay_nodes)

    trip_details = {}
    for group_number, details in optimal_paths.items():
        path = details['full_path']
        order_nodes = details['optimal_order']
        departure_time = individuals_df[individuals_df['Group Number'] == group_number].iloc[0]['Trip Departure Time']
        current_time = pd.to_datetime(departure_time)
        trip_info = []
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            distance = nx.shortest_path_length(G, source, target, weight='length')
            travel_time = calculate_travel_time(distance, AV_SPEED_MPH)
            if random.random() < TRIP_DELAY_PROBABILITY:
                travel_time += TRIP_DELAY_MINUTES
            if node_coords[source] in delay_nodes_set or node_coords[target] in delay_nodes_set:
                travel_time += delay_time
            stop_time = STOP_TIME_MINUTES if source in order_nodes else 0
            current_time += pd.Timedelta(minutes=travel_time + stop_time)
            trip_info.append((source, target, distance, travel_time, current_time.strftime('%H:%M')))
        trip_details[group_number] = trip_info
    return trip_details

# Define the coordinates that will trigger a delay
delay_nodes = ['183760220', '185230194', '185230266', '185231526', '185243366', '185243786', '185247019', 
               '185256313', '185261837', '185261889', '3229016868', '185251914', '185258510', '185246345', 
               '185231466', '185250935', '185251949', '185283598', '185283552', '185245093', '185251914', 
               '185251949', '185251995', '185230194', '185245093', '185250333', '3229016868', '185245164', 
               '185230138', '185249076']

# Define the delay time in minutes
delay_time = 5

# Example use of the function
trip_results = process_trips(G, optimal_paths, individuals_df, delay_nodes, delay_time)

# Printing trip details for each group
for group, trips in trip_results.items():
    print(f"Group {group}:")
    for trip in trips:
        print(f"  From {trip[0]} to {trip[1]}, Travel Time: {trip[3]:.2f} minutes, Arrival Time: {trip[4]}")

# Create DataFrame to export to Excel
columns = ['Group Number', 'From Node', 'To Node', 'Distance (meters)', 'Travel Time (minutes)', 'Arrival Time', 'From Node in Optimal Order', 'To Node in Optimal Order']
data = []
for group, details in trip_results.items():
    for trip in details:
        # Check if the nodes are in the optimal order for this group
        from_node_in_optimal = "Yes" if trip[0] in optimal_paths[group]['optimal_order'] else "No"
        to_node_in_optimal = "Yes" if trip[1] in optimal_paths[group]['optimal_order'] else "No"
        data.append([group] + list(trip) + [from_node_in_optimal, to_node_in_optimal])

df = pd.DataFrame(data, columns=columns)

# Export to Excel
output_file_path = "TripDetails_Group3.xlsx"
df.to_excel(output_file_path, index=False)
output_file_path

def calculate_average_trip_length(trip_results):
    total_duration = timedelta()
    trip_count = 0
    
    for group, trips in trip_results.items():
        for trip in trips:
            # Assuming the format of each trip is (source, target, distance, travel_time, arrival_time)
            # And that travel_time is in minutes and arrival_time is a string in '%H:%M' format
            departure_time = pd.to_datetime(trip[4], format='%H:%M') - pd.Timedelta(minutes=trip[3])
            arrival_time = pd.to_datetime(trip[4], format='%H:%M')
            trip_duration = arrival_time - departure_time
            total_duration += trip_duration
            trip_count += 1
    
    # Calculate the average duration
    average_duration = total_duration / trip_count if trip_count else timedelta()
    return average_duration

# Calculate the average trip length using the function
average_trip_length = calculate_average_trip_length(trip_results)
print(f"The average length of each AV trip is {average_trip_length:.2f} minutes.")
