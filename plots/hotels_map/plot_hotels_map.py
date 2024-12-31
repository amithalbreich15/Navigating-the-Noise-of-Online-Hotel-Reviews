import geopandas
import matplotlib.pyplot as plt
from shapely.geometry import Point

hotel_locations = {
    "Istanbul": (41.0082, 28.9784),
    "Dallas": (32.7767, -96.7970),
    "Budapest": (47.4979, 19.0402),
    "Bangkok": (13.7563, 100.5018),
    "Seattle": (47.6062, -122.3321),
    "Manila": (14.5995, 120.9842),
    "El Calafate": (-50.3379, -72.2648),
    "Mexico City": (19.4326, -99.1332),
    "Kuala Lumpur": (3.1390, 101.6869),
    "Miami": (25.7617, -80.1918),
    "Bergen": (60.3913, 5.3221),
    "Houston": (29.7604, -95.3698),
    "Copenhagen": (55.6761, 12.5683),
    "Lima": (-12.0464, -77.0428),
    "Atlanta": (33.7490, -84.3880),
    "Singapore": (1.3521, 103.8198),
    "London": (51.5074, -0.1278),
    "Riyadh": (24.7136, 46.6753),
    "Madrid": (40.4168, -3.7038),
    "Dar Es Salaam": (-6.7924, 39.2083),
    "Perth": (-31.9505, 115.8605),
    "San Francisco": (37.7749, -122.4194),
    "Bucharest": (44.4268, 26.1025),
    "Philadelphia": (39.9526, -75.1652),
    "Chicago": (41.8781, -87.6298),
    "Beijing": (39.9042, 116.4074),
    "Innsbruck": (47.2692, 11.4041),
    "Bogotá": (4.7110, -74.0721),
    "New York": (40.7128, -74.0060),
    "Lisbon": (38.7223, -9.1393),
    "Barcelona": (41.3851, 2.1734),
    "Warsaw": (52.2297, 21.0122),
    "Ho Chi Minh City": (10.8231, 106.6297),
    "Seoul": (37.5665, 126.9780),
    "Lagos": (6.5244, 3.3792),
    "Santiago": (-33.4489, -70.6693),
    "Rome": (41.9028, 12.4964),
    "New Delhi": (28.6139, 77.2090),
    "Toronto": (43.651070, -79.347015),
    "Fairbanks": (64.8378, -147.7164),
    "Athens": (37.9838, 23.7275),
    "Tromsø": (69.6492, 18.9560),
    "Stockholm": (59.3293, 18.0686),
    "Berlin": (52.5200, 13.4050),
    "Manchester": (53.4808, -2.2426),
    "Paris": (48.8566, 2.3522),
    "Cairo": (30.0444, 31.2357),
    "Taupo": (-38.6857, 176.0702),
    "Cape Town": (-33.9249, 18.4241),
    "Tokyo": (35.6762, 139.6503),
    "Glasgow": (55.8642, -4.2518),
    "Riga": (56.9496, 24.1052)
}

if __name__ == '__main__':
    geometry = [Point(lon, lat) for lat, lon in hotel_locations.values()]
    gdf = geopandas.GeoDataFrame(list(hotel_locations.keys()), geometry=geometry, columns=["Hotel"])
    worldmap = geopandas.read_file('ne_110m_admin_0_countries.zip')

    fig, ax = plt.subplots()
    worldmap.plot(color="lightgrey", ax=ax)
    gdf.plot(ax=ax, color='royalblue', marker='o', markersize=7)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    plt.savefig('hotels_world_map.png')
    plt.tight_layout()
    plt.show()
