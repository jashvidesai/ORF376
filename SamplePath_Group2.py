import networkx as nx
import matplotlib.pyplot as plt

# Load the graph
G = nx.read_graphml('Midland_road_network2.graphml')

# Ensure all 'length' attributes are floats
for u, v, data in G.edges(data=True):
    data['length'] = float(data.get('length', 1))  # Default to 1 if no length

# Nodes sequence for optimal path (Group 52)
nodes_sequence = ['185275807', '185276382', '185303893', '2688570996', '185268911']

# Calculate full path including all intermediate nodes (Group 52)
full_path = [
    '185275807', '185266816', '185228127', '185275809', '185275811',
    '185275815', '185266366', '185266361', '185266347', '185266332',
    '185264226', '185276359', '185276373', '185276382', '185276373',
    '185276359', '185264226', '185266332', '185266347', '185266361',
    '185266366', '185275819', '185275821', '185275823', '185278129',
    '185278137', '185278140', '185278144', '185272465', '185278151',
    '185245120', '185249049', '185278158', '185272407', '185272397',
    '185272383', '185303893', '185306276', '185264425', '185264429',
    '185272030', '185272026', '185272021', '185271995', '185269414',
    '185274671', '185274667', '185286637', '185296431', '185296418',
    '185279694', '185261683', '185273264', '185294227', '3380567843',
    '185301958', '185261368', '185283416', '185245201', '2688570995',
    '2688570996', '185263561', '185264209', '185282587', '185282583',
    '185282579', '185272792', '185282573', '185282567', '185282563',
    '185282559', '185261420', '185269465', '185282553', '185268809',
    '185268962', '185261029', '185261025', '185264356', '185228959',
    '185268920', '185268917', '185268914', '185268911'
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