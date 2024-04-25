import itertools
import random
import networkx as nx
import pandas as pd

AV_SPEED_MPH = 60
STOP_TIME_MINUTES = 2
TRIP_DELAY_PROBABILITY = 0.01
TRIP_DELAY_MINUTES = 5
METERS_PER_MILE = 1609.34

G = nx.read_graphml('Midland_road_network2.graphml')
G = G.to_undirected()

for u, v, data in G.edges(data=True):
    data['length'] = float(data.get('length', 1))

# Define schools
schools = {
    'Midland HS': (-84.2124, 43.6202),
    'Dow HS': (-84.275447, 43.639836),
    'Jefferson MS': (-84.2346, 43.6504),
    'Northeast MS': (-84.2114, 43.6332)
}

schools['Midland HS'] = '185279147'
schools['Dow HS'] = '185275807'
schools['Jefferson MS'] = '185277799'
schools['Northeast MS'] = '185247351'

# Students
students_df = pd.read_excel('School2GroupsUpdated.xlsx')
students_df['Node'] = students_df['Node'].astype(str)
students_df['Trip Departure Time'] = pd.to_datetime(students_df['Trip Departure Time'], format='%H:%M')

# Group nodes together from the assigned groupings with schools being in appropriate positions
groups_nodes = {}
for group_number, group_df in students_df.groupby('Group Number'):
    group_nodes = []

    school_location = group_df.iloc[0]['School Location']
    school_node = schools[school_location]

    # Check the 'Trip Type' for any student in the group to decide the position of the school node
    trip_type = group_df.iloc[0]['Trip Type']

    # all trips are School -> House
    if trip_type == 'School -> House':
        group_nodes.append(school_node)
    group_nodes.extend(group_df['Node'].tolist())
    
    #if trip_type == 'House -> School':
        #group_nodes.append(school_node)
    
    groups_nodes[group_number] = group_nodes

# Function to calculate total path length including intermediate nodes
def calculate_total_path_length(G, path):
    total_length = 0
    for i in range(len(path) - 1):
        total_length += nx.shortest_path_length(G, source=path[i], target=path[i + 1], weight='length')
    return total_length

# Function to get the full path including all intermediate nodes
def get_full_path(G, path):
    full_path = []
    for i in range(len(path) - 1):
        part_path = nx.shortest_path(G, source=path[i], target=path[i + 1], weight='length')
        full_path.extend(part_path if not full_path else part_path[1:])
    return full_path

# Iterate over groups and find the optimal path for each
optimal_paths = {}
for group_number, nodes in groups_nodes.items():
    min_length = float('inf')
    optimal_order = None
    optimal_full_path = None
    
    # Determine the fixed node (school) and the nodes to permute
    if nodes[0] in schools.values():  # School -> House
        fixed_node = nodes[0]
        nodes_to_permute = nodes[1:]
    else:  # House -> School
        fixed_node = nodes[-1]
        nodes_to_permute = nodes[:-1]

    # Generate permutations, keeping the school node fixed
    for permutation in itertools.permutations(nodes_to_permute):
        current_order = [fixed_node] + list(permutation) if fixed_node == nodes[0] else list(permutation) + [fixed_node]
        current_length = calculate_total_path_length(G, current_order)
        
        if current_length < min_length:
            min_length = current_length
            optimal_order = current_order
            optimal_full_path = get_full_path(G, current_order)
    
    # Store the results for this group
    optimal_paths[group_number] = {
        'optimal_order': optimal_order,
        'optimal_full_path': optimal_full_path,
        'total_distance': min_length
    }

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

def process_trips(G, optimal_paths, students_df, delay_nodes, delay_time):
    node_coords = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
    delay_nodes_set = set(delay_nodes)

    trip_details = {}
    for group_number, details in optimal_paths.items():
        path = details['optimal_full_path']
        order_nodes = details['optimal_order']
        departure_time = students_df[students_df['Group Number'] == group_number].iloc[0]['Trip Departure Time']
        current_time = pd.to_datetime(departure_time)
        trip_info = []

        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            distance = nx.shortest_path_length(G, source, target, weight='length')
            travel_time = calculate_travel_time(distance)

            if random.random() < TRIP_DELAY_PROBABILITY:
                travel_time += TRIP_DELAY_MINUTES

            if node_coords[source] in delay_nodes_set or node_coords[target] in delay_nodes_set:
                travel_time += delay_time

            # Only add stop time if the node is in the optimal order list
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
trip_results = process_trips(G, optimal_paths, students_df, delay_nodes, delay_time)

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
output_file_path = "TripDetails_Group2.xlsx"
df.to_excel(output_file_path, index=False)
output_file_path