from datetime import timedelta
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Load the graph
G = nx.read_graphml('Midland_road_network4.graphml')

# Ensure all 'length' attributes are floats
for u, v, data in G.edges(data=True):
    data['length'] = float(data.get('length', 1))  # Default to 1 if no length

# Nodes sequence for optimal path (Group 3)
nodes_sequence = ['185303772', '185299203', '185263640', '185311513', '183690722']

# Calculate full path including all intermediate nodes (Group 3)
full_path = ['185303772', '185273002', '185266164', '4121305179', '185266106', '185266098', '185266083', '185266080', '1083071630', '185314063', '185261859', '185281264', '185276111', '185314055', '185299203', '185299192', '185268954', '185266069', '185283322', '185301034', '185268909', '185268911', '185268914', '185268917', '185268920', '185228959', '185264356', '185261025', '185261029', '185268962', '185268809', '185282553', '185269465', '185261420', '185282559', '185282563', '185282567', '185282573', '185272792', '185282579', '185282583', '185282587', '185264209', '185263561', '2145766066', '185276061', '185263599', '185289892', '185258735', '185289890', '185289887', '185289885', '185288375', '185266241', '185299902', '185276730', '185296099', '185269881', '185269885', '185268067', '185310879', '185280218', '185263640', '185313963', '185296878', '185296776', '185296779', '185296616', '185291660', '185291653', '185311524', '185228407', '185299402', '185304273', '185311513', '185311511', '185279339', '185264163', '185274294', '185264720', '185264716', '185263025', '185290997', '185290993', '185275143', '185283577', '185283574', '185283568', '185281041', '185283562', '185283559', '185279059', '185283554', '3279602695', '185283552', '185260789', '185248554', '185272901', '185272900', '185272899', '185306931', '185284534', '185305126', '3895864233', '185287692', '185306928', '185282433', '185306916', '3175957607', '3175957606', '185294428', '183695446', '183690806', '183690722']

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