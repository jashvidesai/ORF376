from matplotlib import pyplot as plt
from shapely.geometry import Polygon
import geopandas as gpd
import osmnx as ox
import networkx as nx
import random

# Specify the location and create a graph from OpenStreetMap data
location = "Midland County, Michigan, USA"
G = ox.graph_from_place(location, network_type='drive')

# Convert the graph to undirected for centrality calculations
G_undirected = G.to_undirected()

nodes_data = [{'node': node, 'x': data['x'], 'y': data['y']} for node, data in G.nodes(data=True)]
nodes_gdf = gpd.GeoDataFrame(nodes_data, geometry=gpd.points_from_xy([node['x'] for node in nodes_data], [node['y'] for node in nodes_data]))

# Define regions
regions = {
    'EM': Polygon([(-84.2271, 43.6560), (-84.2119, 43.6557), (-84.1907, 43.6451), (-84.1770, 43.6263), (-84.2271, 43.6266)]),
    'NM': Polygon([(-84.227, 43.6413), (-84.2952, 43.6425), (-84.3072, 43.6558), (-84.2897, 43.6566), (-84.2896, 43.6620), 
                   (-84.2882, 43.6623), (-84.2823, 43.6658), (-84.2771, 43.6666), (-84.271, 43.6694), (-84.277, 43.6694), 
                   (-84.2621, 43.6695), (-84.2671, 43.6566), (-84.2272, 43.6563), (-84.2272, 43.6640), (-84.2171, 43.6638), 
                   (-84.2175, 43.6583), (-84.227, 43.6581), (-84.227, 43.6564), (-84.227, 43.6564)]),
    'WM': Polygon([(-84.2952, 43.6425), (-84.2468, 43.6417), (-84.2473, 43.613), (-84.2699, 43.6123), (-84.3127, 43.6115), 
                   (-84.3103, 43.6377), (-84.2996, 43.6378), (-84.2996, 43.6413)]),
    'SM': Polygon([(-84.1675, 43.6266), (-84.2269, 43.6265), (-84.2273, 43.6116), (-84.1874, 43.6112), (-84.1876, 43.6049), 
                   (-84.2076, 43.6050), (-84.2076, 43.6010), (-84.2030, 43.5984), (-84.1877, 43.5979), (-84.1788, 43.5982), 
                   (-84.1777, 43.6030), (-84.1776, 43.6070), (-84.1754, 43.6087), (-84.1653, 43.6086), (-84.1696, 43.6159), 
                   (-84.1795, 43.6158), (-84.1795, 43.6147), (-84.1818, 43.6147), (-84.1818, 43.6143), (-84.1825, 43.6143), 
                   (-84.2073, 43.6125), (-84.2072, 43.6195), (-84.1973, 43.6194), (-84.1954, 43.6208), (-84.1875, 43.6211), 
                   (-84.1874, 43.6265), (-84.1773, 43.6264)]),
    'CM': Polygon([(-84.2468, 43.6417), (-84.2475, 43.5976), (-84.2465, 43.6048), (-84.2434, 43.6095), (-84.241, 43.6107), 
                   (-84.2384, 43.6125), (-84.2362, 43.6103), (-84.2329, 43.6095), (-84.2274, 43.6118), (-84.227, 43.6413)])
}

# Calculate centrality measures
degree_centrality = nx.degree_centrality(G_undirected)
betweenness_centrality = nx.betweenness_centrality(G_undirected)
closeness_centrality = nx.closeness_centrality(G_undirected)

# Function to get top 10 nodes for each centrality measure
def get_top_nodes(centrality_dict):
    return sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)[:10]

# Get top 10 nodes for each centrality measure
top_degree = get_top_nodes(degree_centrality)
top_betweenness = get_top_nodes(betweenness_centrality)
top_closeness = get_top_nodes(closeness_centrality)

# Retrieve coordinates for top nodes
def get_coordinates(graph, nodes):
    coords = {node: (graph.nodes[node]['y'], graph.nodes[node]['x']) for node in nodes}
    return coords

top_degree_coords = get_coordinates(G, [node[0] for node in top_degree])
top_betweenness_coords = get_coordinates(G, [node[0] for node in top_betweenness])
top_closeness_coords = get_coordinates(G, [node[0] for node in top_closeness])

# Function to print node details including centrality values
def print_node_details(title, top_nodes, coordinates):
    print(title + ":")
    for node, centrality in top_nodes:
        coord = coordinates[node]
        # Ensure that the variable name matches the loop variable 'centrality'
        print(f"Node {node}, Coordinates: ({coord[1]}, {coord[0]}), Centrality Value: {centrality:.6f}")
    print()

# Visualize the graph with top nodes highlighted
fig, ax = ox.plot_graph(G, node_color='gray', node_size=5, show=False, close=False)
# Prepare top node lists for each centrality
top_degree_nodes = set([node for node, _ in top_degree])
top_betweenness_nodes = set([node for node, _ in top_betweenness])
top_closeness_nodes = set([node for node, _ in top_closeness])

# Assign colors to nodes based on their centrality rankings
nc = []
for node in G.nodes():
    if node in top_degree_nodes:
        nc.append('red')  # red for top degree centrality nodes
    elif node in top_betweenness_nodes:
        nc.append('blue')  # blue for top betweenness centrality nodes
    elif node in top_closeness_nodes:
        nc.append('green')  # green for top closeness centrality nodes
    else:
        nc.append('gray')  # gray for all other nodes

# Node sizes
ns = [50 if node in top_degree_nodes or node in top_betweenness_nodes or node in top_closeness_nodes else 5 for node in G.nodes()]

# Draw the graph with the specified node colors and sizes
ox.plot_graph(G, ax=ax, node_color=nc, node_size=ns, edge_linewidth=0.5)
plt.show()

(top_degree_coords, top_betweenness_coords, top_closeness_coords)
# Print details for each centrality measure
print_node_details("Top Degree Centrality Nodes", top_degree, top_degree_coords)
print_node_details("Top Betweenness Centrality Nodes", top_betweenness, top_betweenness_coords)
print_node_details("Top Closeness Centrality Nodes", top_closeness, top_closeness_coords)

if nx.is_connected(G_undirected):
    avg_path_length = nx.average_shortest_path_length(G_undirected)
    print("Average path length:", avg_path_length)
else:
    print("Graph is not connected. Considering the largest connected component.")

    # Get the largest connected component (for undirected graphs)
    largest_cc = max(nx.connected_components(G_undirected), key=len)
    subgraph = G_undirected.subgraph(largest_cc)
    avg_path_length = nx.average_shortest_path_length(subgraph)
    print("Average path length in the largest connected component:", avg_path_length)

for region_name, polygon in regions.items():
    # Filter nodes within the polygon
    nodes_within_region = nodes_gdf[nodes_gdf.within(polygon)]
    
    # Check if there are enough nodes to calculate path lengths
    if len(nodes_within_region) > 1:
        subgraph = G.subgraph(nodes_within_region['node'])
        # Assuming 'subgraph' is the directed subgraph you're analyzing
        if nx.is_strongly_connected(subgraph):
            avg_path_length = nx.average_shortest_path_length(subgraph)
            print(f"Average path length in {region_name}: {avg_path_length}")
        else:
            print(f"Subgraph in {region_name} is not strongly connected.")
            # Extract the largest strongly connected component
            largest_scc = max(nx.strongly_connected_components(subgraph), key=len)
            scc_subgraph = subgraph.subgraph(largest_scc)
            if nx.is_strongly_connected(scc_subgraph):
                avg_path_length = nx.average_shortest_path_length(scc_subgraph)
                print(f"Average path length in the largest SCC of {region_name}: {avg_path_length}")
            else:
                print(f"Even the largest SCC in {region_name} is not strongly connected, which should not happen.")
    else:
        print(f"Not enough nodes in {region_name} to calculate path lengths.")

