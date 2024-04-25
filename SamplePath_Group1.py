import networkx as nx
import matplotlib.pyplot as plt

# Load the graph
G = nx.read_graphml('Midland_road_network1.graphml')

# Ensure all 'length' attributes are floats
for u, v, data in G.edges(data=True):
    data['length'] = float(data.get('length', 1))  # Default to 1 if no length

# Nodes sequence for optimal path (Group 9)
nodes_sequence = ['185287049', '185305338', '185293344', '185261626', '185275807']

# Calculate full path including all intermediate nodes (Group 6)
full_path = [
    '185287049', '185319264', '185308963', '185303506', '185294988', 
    '185263103', '185286557', '185305338', '185295920', '185272789', 
    '185287930', '185299799', '2055082391', '185300953', '2055082390', 
    '185228244', '2075250727', '185263555', '2145766066', '2688570996', 
    '2688570995', '185245201', '185283416', '185261368', '185301958', 
    '185275052', '185268856', '185294233', '185293344', '185283053', 
    '185276646', '185273264', '185261683', '185261626', '185261683', 
    '185279694', '185296418', '185301992', '2296216338', '185302009', 
    '185302013', '185302030', '185272574', '185302033', '185294637', 
    '185295202', '2376125974', '185302039', '185302048', '185289982', 
    '185266212', '185275807'
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