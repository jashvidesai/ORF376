from datetime import timedelta
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

from PathAssigner_Group3 import trip_results

# Load the graph
G = nx.read_graphml('Midland_road_network3.graphml')

# Ensure all 'length' attributes are floats
for u, v, data in G.edges(data=True):
    data['length'] = float(data.get('length', 1))  # Default to 1 if no length

# Nodes sequence for optimal path (Group 4)
nodes_sequence = ['185280842', '1490943108', '185287558', '1490943108', '185271091', '1490943108', '185297115', '185246034']

# Calculate full path including all intermediate nodes (Group 52)
full_path = [
    '185280842', '185279147', '185279151', '185279155', '185279159', '185291595', '185291598', '2688579274', '185263614', '185276061', '185257751', '185282291', '3180222481', '185282310', '185279549', '185265998', '185261374', '185279258', '185286840', '185280224', '185300936', '185295487', '185280971', '185263882', '185278018', '185294484', '185264583', '185246079', '185300937', '185269757', '3269834948', '185278166', '2083706644', '185265380', '1490942881', '3284647497', '1490942082', '1490943108', '1490942082', '3284647497', '1490942881', '185265380', '2083706644', '185278166', '3269834948', '185269757', '185300937', '185246079', '185264583', '185294484', '185278018', '185263882', '185280971', '185295487', '185300936', '185280224', '185286840', '185279258', '185261374', '185265998', '185279549', '185282310', '3180222481', '185282291', '185257751', '185276061', '2145766066', '185263555', '2075250727', '185228244', '2055082390', '185300953', '2055082391', '185299799', '185287930', '185272789', '185295920', '185305338', '185282659', '185290675', '185277350', '185294991', '185287558', '185294991', '185277350', '185290675', '185282659', '185305338', '185295920', '185272789', '185287930', '185299799', '2055082391', '185300953', '2055082390', '185228244', '2075250727', '185263555', '2145766066', '185276061', '185257751', '185282291', '3180222481', '185282310', '185279549', '185265998', '185261374', '185279258', '185286840', '185280224', '185300936', '185295487', '185280971', '185263882', '185278018', '185294484', '185264583', '185246079', '185300937', '185269757', '3269834948', '185278166', '2083706644', '185265380', '1490942881', '3284647497', '1490942082', '1490943108', '185274600', '1923265980', '3284569183', '3171063288', '185275231', '185311062', '3170945272', '185275214', '3213243661', '185311197', '3170958741', '185311070', '185243458', '185252476', '185245185', '185257329', '185278158', '185266713', '185274420', '185273202', '185305347', '185308123', '185285558', '185288303', '185302013', '185294911', '3804340448', '3804340435', '185294889', '185294893', '185304498', '185294180', '185271042', '185271091', '185271042', '185294180', '185304498', '185294893', '185294889', '3804340435', '3804340448', '185294911', '185302013', '185288303', '185285558', '185308123', '185305347', '185273202', '185274420', '185266713', '185278158', '185257329', '185245185', '185252476', '185243458', '185311070', '3170958741', '185311197', '3213243661', '185275214', '3170945272', '185311062', '185275231', '3171063288', '3284569183', '1923265980', '185274600', '1490943108', '1490942082', '3284647497', '1490942881', '185265380', '2083706644', '185278166', '3269834948', '185269757', '185300937', '185246079', '185264583', '185294484', '185278018', '185263882', '185280971', '185295487', '185300936', '185280224', '185286840', '185279258', '185261374', '185265998', '185279549', '185279545', '185302340', '185289892', '185258723', '185297115', '185258723', '185289892', '185302340', '185279545', '185279549', '185265998', '185261374', '185279258', '185286840', '185280224', '185300936', '185295487', '185280971', '185263882', '185278018', '185294484', '185264583', '185246079', '185300937', '185269757', '3269834948', '185278166', '2083706644', '185265380', '1490942881', '3284647497', '1490942082', '1490943108'
]

# Function to plot the full path
def plot_full_path(G, full_path, nodes_sequence):
    pos = {node: (float(G.nodes[node]['x']), float(G.nodes[node]['y'])) for node in G.nodes()}
    fig, ax = plt.subplots(figsize=(12, 10))

    nx.draw(G, pos, node_size=2, edge_color='grey', width=1, with_labels=False, arrows=False)
    nx.draw_networkx_nodes(G, pos, nodelist=full_path, node_color='blue', node_size=50) # Highlight the whole path

    sequence_pos = {node: pos[node] for node in nodes_sequence}
    nx.draw_networkx_nodes(G, sequence_pos, nodelist=nodes_sequence, node_color='green', node_size=100, edgecolors='black', linewidths=2)

    nx.draw_networkx_edges(G, pos, edgelist=list(zip(full_path[:-1], full_path[1:])), edge_color='red', width=2, arrowstyle='-|>', arrowsize=15)

    for index, node in enumerate(nodes_sequence):
        plt.text(*pos[node], s=str(index+1), horizontalalignment='center', verticalalignment='center', fontsize=9, fontweight='bold', color='white')
    
    # Zoom
    margin = 0.05  # 5% margin
    all_x_values = [pos[n][0] for n in full_path]
    all_y_values = [pos[n][1] for n in full_path]
    x_range = max(all_x_values) - min(all_x_values)
    y_range = max(all_y_values) - min(all_y_values)
    ax.set_xlim(min(all_x_values) - margin*x_range, max(all_x_values) + margin*x_range)
    ax.set_ylim(min(all_y_values) - margin*y_range, max(all_y_values) + margin*y_range)

    ax.axis('off')
    plt.show()

# Plot the full path on the graph
plot_full_path(G, full_path, nodes_sequence)

# also calculate the average trip length
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