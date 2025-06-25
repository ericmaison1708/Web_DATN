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

# Earth radius in kilometers
earth_radius_km = 6371.0

# Load metadata and build BallTrees at startup
def load_data(filename):
    df = pd.read_csv(os.path.join(DATA_DIR, filename), usecols=['Name', 'Address', 'latitude', 'longitude'], low_memory=False)
    df = df.dropna(subset=['latitude', 'longitude']).reset_index(drop=True)
    coords_rad = np.deg2rad(df[['latitude', 'longitude']].values)
    tree = BallTree(coords_rad, metric='haversine')
    return df, tree

# Load hotels and restaurants trees
df_hotels, hotel_tree = load_data('hotels.csv')
df_restaurants, rest_tree = load_data('restaurants.csv')
# Try attractions, fallback to empty
def load_attractions():
    try:
        df, tree = load_data('attractions.csv')
        return df, tree
    except Exception:
        return None, None

df_attractions, attr_tree = load_attractions()

# Query function: get sorted neighbors within radius
def query_tree(tree, df_meta, lat, lon, radius_km, top_n=10):
    # Convert point to radians
    pt_rad = np.deg2rad([[lat, lon]])
    # Query all points for sorted distances
    total = df_meta.shape[0]
    dists_rad, inds = tree.query(pt_rad, k=total)
    dists_km = dists_rad[0] * earth_radius_km
    idxs = inds[0]
    # Filter by radius
    mask = dists_km <= radius_km
    filtered_idxs = idxs[mask]
    filtered_dists = dists_km[mask]
    # Take top_n
    pairs = list(zip(filtered_idxs, filtered_dists))[:top_n]
    results = []
    for idx, dist in pairs:
        meta = df_meta.iloc[idx].to_dict()
        meta['distance'] = round(float(dist), 2)
        results.append(meta)
    return results

@app.route('/')
def home():
    return "EricTravel Backend API is running."

@app.route('/api/search_hotels')
def search_hotels():
    address = request.args.get('address', '')
    radius = float(request.args.get('radius', 10))
    loc = geolocator.geocode(address)
    if not loc:
        return jsonify({'status': 'fail', 'message': 'Không tìm thấy địa điểm'})
    results = query_tree(hotel_tree, df_hotels, loc.latitude, loc.longitude, radius)
    return jsonify({'status': 'success', 'hotels': results})

@app.route('/api/search_restaurants')
def search_restaurants():
    address = request.args.get('address', '')
    radius = float(request.args.get('radius', 10))
    loc = geolocator.geocode(address)
    if not loc:
        return jsonify({'status': 'fail', 'message': 'Không tìm thấy địa điểm'})
    results = query_tree(rest_tree, df_restaurants, loc.latitude, loc.longitude, radius)
    return jsonify({'status': 'success', 'restaurants': results})

@app.route('/api/search_attractions')
def search_attractions():
    address = request.args.get('address', '')
    radius = float(request.args.get('radius', 10))
    loc = geolocator.geocode(address)
    if not loc:
        return jsonify({'status': 'fail', 'message': 'Không tìm thấy địa điểm'})
    if attr_tree is not None:
        results = query_tree(attr_tree, df_attractions, loc.latitude, loc.longitude, radius)
    else:
        results = []
    return jsonify({'status': 'success', 'attractions': results})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
