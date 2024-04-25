import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import networkx as nx
from shapely.geometry.base import BaseGeometry
from shapely import wkt

G = nx.read_graphml('Midland_road_network1.graphml')

for node, data in G.nodes(data=True):
    try:
        data['x'] = float(data['x'])
        data['y'] = float(data['y'])
    except ValueError as e:
        print(f"Error converting node {node} coordinates to float: {e}")

def ensure_geometry(data):
    if isinstance(data, str):
        try:
            geom = wkt.loads(data)
            if not geom.is_valid:
                geom = geom.buffer(0)
            return geom
        except Exception as e:
            print(f"Error converting WKT to Geometry: {e}")
            return None
    elif isinstance(data, BaseGeometry):
        if not data.is_valid:
            return data.buffer(0)
        return data
    return None
    
# Validate and fix geometries in the graph
for u, v, key, data in G.edges(keys=True, data=True):
    if 'geometry' in data:
        geom = ensure_geometry(data['geometry'])
        if geom is None or not geom.is_valid:
            data['geometry'] = None
        else:
            data['geometry'] = geom

nodes_data = [{'node': node, 'x': data['x'], 'y': data['y']} for node, data in G.nodes(data=True)]
nodes_gdf = gpd.GeoDataFrame(nodes_data, geometry=gpd.points_from_xy([node['x'] for node in nodes_data], [node['y'] for node in nodes_data]))

students_df = pd.read_excel('School1Groups.xlsx')

# regions
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

students_df['Node'] = None
students_df['Coordinates'] = None

# Assign unique locations per student ID
unique_locations = {}

# function to find a random node within a given region
def get_random_node_within_polygon(polygon, nodes):
    potential_nodes = nodes[nodes.within(polygon)]
    return potential_nodes.sample(1).iloc[0] if not potential_nodes.empty else None

# Iterate over unique student IDs
for student_id in students_df['ID'].unique():
    student_rows = students_df[students_df['ID'] == student_id]
    region_name = student_rows.iloc[0]['House Location']
    region_polygon = regions.get(region_name, None)
    
    if region_polygon is not None:
        random_node = get_random_node_within_polygon(region_polygon, nodes_gdf)
        if random_node is not None:
            unique_locations[student_id] = {
                'Node': random_node['node'],
                'Coordinates': (random_node['x'], random_node['y'])
            }

# Update the DataFrame with the assigned locations
for i, row in students_df.iterrows():
    student_id = row['ID']
    if student_id in unique_locations:
        students_df.at[i, 'Node'] = unique_locations[student_id]['Node']
        students_df.at[i, 'Coordinates'] = unique_locations[student_id]['Coordinates']

# save to Excel
students_df.to_excel('School1GroupsUpdated.xlsx', index=False)