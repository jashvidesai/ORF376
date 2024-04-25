import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# Define the location coordinates
destinations = {
    'Meijer': (-84.2432, 43.6632),
    'Walmart': (-84.2381, 43.6614),
    'Aldi': (-84.24142, 43.66200),
    'Kroger': (-84.2284, 43.6246),
    'MidMichigan Health': (-84.2606, 43.6351),
    'Dow Family Center': (-84.23909, 43.61011),
    'Target': (-84.24111, 43.65876)
}

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame([
    {'Name': name, 'Longitude': lon, 'Latitude': lat}
    for name, (lon, lat) in destinations.items()
],
geometry=gpd.points_from_xy([lon for lon, lat in destinations.values()],
                            [lat for lon, lat in destinations.values()]))

# Set the CRS for WGS84 (lat/long)
gdf.crs = "EPSG:4326"

# Convert to Web Mercator for plotting on OSM
gdf = gdf.to_crs(epsg=3857)

# Plotting
fig, ax = plt.subplots(figsize=(12, 8))  # Adjust figure size to make it wider
gdf.plot(ax=ax, marker='o', color='red', markersize=50)  # Adjust marker size as needed

# Add labels
for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf['Name']):
    ax.text(x + 100, y + 100, label, fontsize=12, ha='left', color='blue')  # Offset labels to avoid overlap

# Add basemap
ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Remove axes
ax.set_axis_off()

plt.show()