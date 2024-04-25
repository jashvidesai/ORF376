import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# Define the location coordinates
destinations = {
    'Dow Chemical Plant': (-84.2275, 43.6055),
    'Midland Wastewater Treatment Center': (-84.2006, 43.6077),
}

gdf = gpd.GeoDataFrame([
    {'Name': name, 'Longitude': lon, 'Latitude': lat}
    for name, (lon, lat) in destinations.items()
],
geometry=gpd.points_from_xy([lon for lon, lat in destinations.values()],
                            [lat for lon, lat in destinations.values()]))

gdf.crs = "EPSG:4326"
gdf = gdf.to_crs(epsg=3857)

fig, ax = plt.subplots(figsize=(12, 8))
gdf.plot(ax=ax, marker='o', color='red', markersize=50)

for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf['Name']):
    ax.text(x + 100, y + 100, label, fontsize=12, ha='left', color='blue')

ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

xmin, xmax, ymin, ymax = ax.axis()
dx = (xmax - xmin) * 0.1  # Increase the range by 10%
dy = (ymax - ymin) * 0.1  # Increase the range by 10%
ax.set_xlim(xmin - dx, xmax + dx)
ax.set_ylim(ymin - dy, ymax + dy)

ax.set_axis_off()
plt.show()