from flask import Flask, request, jsonify
from flask_cors import CORS
from geopy.geocoders import Nominatim
from sklearn.neighbors import BallTree
import numpy as np
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Initialize geolocator
geolocator = Nominatim(user_agent="erictravel_backend", timeout=10)

# Path to CSV data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Load metadata and build BallTree once at startup
print("Loading data and building spatial index...")
df_hotels = pd.read_csv(os.path.join(DATA_DIR, 'hotels.csv'), usecols=['Name', 'Address', 'latitude', 'longitude']).dropna()
coords_hotels = np.deg2rad(df_hotels[['latitude', 'longitude']].values)
hotel_tree = BallTree(coords_hotels, metric='haversine')

df_restaurants = pd.read_csv(os.path.join(DATA_DIR, 'restaurants.csv'), usecols=['Name', 'Address', 'latitude', 'longitude']).dropna()
coords_rest = np.deg2rad(df_restaurants[['latitude', 'longitude']].values)
rest_tree = BallTree(coords_rest, metric='haversine')

try:
    df_attractions = pd.read_csv(os.path.join(DATA_DIR, 'attractions.csv'), usecols=['Name', 'Address', 'latitude', 'longitude']).dropna()
    coords_attr = np.deg2rad(df_attractions[['latitude', 'longitude']].values)
    attr_tree = BallTree(coords_attr, metric='haversine')
except Exception:
    df_attractions = None
    attr_tree = None

# Earth radius in kilometers
EARTH_RADIUS_KM = 6371.0

# Helper: query nearest within radius_km, return top N records
def query_tree(tree, df_meta, lat, lon, radius_km, top_n=10):
    # Convert to radians
    point_rad = np.deg2rad([[lat, lon]])
    # Radius in radians
    radius_rad = radius_km / EARTH_RADIUS_KM
    # Query indices within radius
    idxs = tree.query_radius(point_rad, r=radius_rad)[0]
    if len(idxs) == 0:
        return []
    # Compute exact distances
    dists_rad, inds = tree.query(point_rad, k=len(idxs))
    dists_km = (dists_rad[0] * EARTH_RADIUS_KM)
    # Pair (index, distance)
    pairs = list(zip(idxs[inds[0]], dists_km))
    # Sort by distance and take top_n
    pairs_sorted = sorted(pairs, key=lambda x: x[1])[:top_n]
    # Build result list
    results = []
    for idx, dist in pairs_sorted:
        meta = df_meta.iloc[idx].to_dict()
        meta['distance'] = round(float(dist), 2)
        results.append(meta)
    return results

@app.route("/")
def home():
    return "EricTravel Backend API is running."

@app.route("/api/search_hotels")
def search_hotels():
    address = request.args.get("address", "")
    radius = float(request.args.get("radius", 10))
    loc = geolocator.geocode(address)
    if not loc:
        return jsonify({'status': 'fail', 'message': 'Không tìm thấy địa điểm'})
    results = query_tree(hotel_tree, df_hotels, loc.latitude, loc.longitude, radius)
    return jsonify({'status': 'success', 'hotels': results})

@app.route("/api/search_restaurants")
def search_restaurants():
    address = request.args.get("address", "")
    radius = float(request.args.get("radius", 10))
    loc = geolocator.geocode(address)
    if not loc:
        return jsonify({'status': 'fail', 'message': 'Không tìm thấy địa điểm'})
    results = query_tree(rest_tree, df_restaurants, loc.latitude, loc.longitude, radius)
    return jsonify({'status': 'success', 'restaurants': results})

@app.route("/api/search_attractions")
def search_attractions():
    address = request.args.get("address", "")
    radius = float(request.args.get("radius", 10))
    loc = geolocator.geocode(address)
    if not loc:
        return jsonify({'status': 'fail', 'message': 'Không tìm thấy địa điểm'})
    if attr_tree is not None:
        results = query_tree(attr_tree, df_attractions, loc.latitude, loc.longitude, radius)
    else:
        results = []
    return jsonify({'status': 'success', 'attractions': results})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Use production-ready server in Render via Procfile/Gunicorn
    app.run(host="0.0.0.0", port=port)
