import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import pandas as pd
from shapely.geometry import Point, Polygon
import random

ox.settings.use_cache = True
ox.settings.log_console = True
ox.settings.default_crs = "EPSG:4326"

dow_high_coords = (-84.275447, 43.639836)  # Dow High School
jefferson_middle_coords = (-84.2346, 43.6504) # Jefferson Middle School
midland_high_coords = (-84.2124, 43.6202)  # Midland High School
northeast_middle_coords = (-84.2114, 43.6332) # Northeast Middle School

# GeoDataFrame for the schools
schools_gdf = gpd.GeoDataFrame({
    'School': ['Dow High School', 'Jefferson Middle School', 'Midland High School', 'Northeast Middle School'],
    'geometry': [Point(dow_high_coords), Point(jefferson_middle_coords), Point(midland_high_coords), Point(northeast_middle_coords)]
}, crs="EPSG:4326")

# defining sections of Midland
EM = Polygon([(-84.2271, 43.6560), (-84.2119, 43.6557), (-84.1907, 43.6451), (-84.1770, 43.6263), 
              (-84.2271, 43.6266)])
NM = Polygon([(-84.227, 43.6413), (-84.2952, 43.6425), (-84.3072, 43.6558), (-84.2897, 43.6566), 
              (-84.2896, 43.6620), (-84.2882, 43.6623), (-84.2823, 43.6658), (-84.2771, 43.6666), 
              (-84.271, 43.6694), (-84.277, 43.6694), (-84.2621, 43.6695), (-84.2671, 43.6566), 
              (-84.2272, 43.6563), (-84.2272, 43.6640), (-84.2171, 43.6638), (-84.2175, 43.6583), 
              (-84.227, 43.6581), (-84.227, 43.6564), (-84.227, 43.6564)])
WM = Polygon([(-84.2952, 43.6425), (-84.2468, 43.6417), (-84.2473, 43.613), (-84.2699, 43.6123), 
              (-84.3127, 43.6115), (-84.3103, 43.6377), (-84.2996, 43.6378), (-84.2996, 43.6413)])
SM = Polygon([(-84.1675, 43.6266), (-84.2269, 43.6265), (-84.2273, 43.6116), (-84.1874, 43.6112),
              (-84.1876, 43.6049), (-84.2076, 43.6050), (-84.2076, 43.6010), (-84.2030, 43.5984), 
              (-84.1877, 43.5979), (-84.1788, 43.5982), (-84.1777, 43.6030), (-84.1776, 43.6070), 
              (-84.1754, 43.6087), (-84.1653, 43.6086), (-84.1696, 43.6159), (-84.1795, 43.6158), 
              (-84.1795, 43.6147), (-84.1818, 43.6147), (-84.1818, 43.6143), (-84.1825, 43.6143), 
              (-84.2073, 43.6125), (-84.2072, 43.6195), (-84.1973, 43.6194), (-84.1954, 43.6208), 
              (-84.1875, 43.6211), (-84.1874, 43.6265), (-84.1773, 43.6264)])
CM = Polygon([(-84.2468, 43.6417), (-84.2475, 43.5976), (-84.2465, 43.6048), (-84.2434, 43.6095), 
              (-84.241, 43.6107), (-84.2384, 43.6125), (-84.2362, 43.6103), (-84.2329, 43.6095), 
              (-84.2274, 43.6118), (-84.227, 43.6413)])

# GeoDataFrame for the areas
areas_gdf = gpd.GeoDataFrame({
    'Area': ['EM', 'NM', 'WM', 'SM', 'CM'],
    'geometry': [EM, NM, WM, SM, CM]
}, crs="EPSG:4326")

trip_data_school2 = pd.read_excel("School2Groups.xlsx")
house_location_mapping = trip_data_school2[['ID', 'House Location']].drop_duplicates().set_index('ID')['House Location'].to_dict()
unique_ids = trip_data_school2['ID'].unique()

# DataFrame for the students
students = pd.DataFrame({
    'ID': unique_ids,
    'Area': [house_location_mapping[id_] for id_ in unique_ids]
})

# load the road network (second plot)
place_name = "Midland, Michigan, USA"
graph = ox.graph_from_place(place_name, network_type='drive')
nodes, edges = ox.graph_to_gdfs(graph)

# Load land use data
land_use = ox.geometries_from_place(place_name, tags={'landuse': True})

# Function to check if a point is not in the green areas
def is_not_in_green_area(point, green_areas):
    for area in green_areas.itertuples():
        if point.within(area.geometry):
            return False
    return True

# Function to assign a random home location, avoiding green areas
def assign_random_home(area, areas_gdf, green_areas):
    selected_area = areas_gdf.loc[areas_gdf['Area'] == area, 'geometry'].squeeze()
    while True:
        random_point = Point(
            random.uniform(selected_area.bounds[0], selected_area.bounds[2]),
            random.uniform(selected_area.bounds[1], selected_area.bounds[3])
        )
        if selected_area.contains(random_point) and is_not_in_green_area(random_point, green_areas):
            return random_point
        
green_areas = land_use[land_use['landuse'].isin(['forest', 'park'])]

# function to assign a random point within a polygon (house locations)
def assign_random_home(area, areas_gdf):
    selected_area = areas_gdf[areas_gdf['Area'] == area].geometry.iloc[0]
    minx, miny, maxx, maxy = selected_area.bounds
    while True:
        pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if selected_area.contains(pnt):
            return pnt

# call the function above
students['Home'] = students['Area'].apply(lambda x: assign_random_home(x, areas_gdf))

# convert students DataFrame to a GeoDataFrame
students_gdf = gpd.GeoDataFrame(students, geometry='Home', crs="EPSG:4326")

# (first) plot with OpenStreetMap as the background
fig, ax = plt.subplots(figsize=(12, 8))
areas_gdf.to_crs(epsg=3857).plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5)

# labels
for idx, row in areas_gdf.to_crs(epsg=3857).iterrows():
    centroid = row['geometry'].centroid
    ax.annotate(row['Area'], xy=(centroid.x, centroid.y), xytext=(3, 3), textcoords="offset points", fontsize=9, ha='center')
schools_gdf.to_crs(epsg=3857).plot(ax=ax, color='red', marker='o', markersize=100)
students_gdf.to_crs(epsg=3857).plot(ax=ax, color='green', marker='x', markersize=5, alpha=0.6)

# add OSM basemap
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# labels for schools (adjust as necessary)
for x, y, label in zip(schools_gdf.geometry.x, schools_gdf.geometry.y, schools_gdf.School):
    ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points", fontsize=9, ha='center')

# first plot
plt.title("Midland Schools and After-School Student Homes on OSM")
ax.set_axis_off()
plt.show()

# second plot
# convert student homes to closest nodes on the road network
students_gdf['closest_node'] = students_gdf.apply(lambda row: ox.distance.nearest_nodes(graph, row['Home'].x, row['Home'].y), axis=1)

# plotting
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(-84.35, -84.15)
ax.set_ylim(43.58, 43.68)

# plot road network
edges.plot(ax=ax, linewidth=1, edgecolor='gray')
areas_gdf.plot(ax=ax, color='none', edgecolor='pink', linewidth=5, alpha=0.5)

# color coding for easier visual representation
area_colors = {'EM': 'purple', 'NM': 'green', 'WM': 'red', 'SM': 'pink', 'CM': 'brown'}
for area, color in area_colors.items():
    areas_gdf[areas_gdf['Area'] == area].plot(ax=ax, color=color, edgecolor=color, linewidth=4, label=area)

# plot student homes and schools
students_gdf.plot(ax=ax, color='blue', marker='o', markersize=5, alpha=0.6, label='Student Homes')
for idx, row in schools_gdf.iterrows():
    ax.plot(row.geometry.x, row.geometry.y, 'o', markersize=7, label=f'{row.School}', color='orange')

    # Annotate each school
    ax.annotate(row.School, xy=(row.geometry.x, row.geometry.y),
                xytext=(5, 5), textcoords="offset points",
                fontsize=9, ha='center', color='black')

# add labels, titles, etc.
plt.title("Midland Road Network with Sections and After-School Student Homes")
plt.legend(title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
ox.save_graphml(graph, 'Midland_road_network2.graphml')
plt.show()