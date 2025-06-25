
from flask import Flask, request, jsonify
from flask_cors import CORS
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Khởi tạo geolocator
geolocator = Nominatim(user_agent="erictravel_backend", timeout=10)

# Load dữ liệu
DATA_DIR = "data"
df_hotels = pd.read_csv(os.path.join(DATA_DIR, "hotels.csv")).dropna(subset=['latitude', 'longitude'])
df_restaurants = pd.read_csv(os.path.join(DATA_DIR, "restaurants.csv")).dropna(subset=['latitude', 'longitude'])
df_attractions = pd.read_csv(os.path.join(DATA_DIR, "attractions.csv")).dropna(subset=['latitude', 'longitude'])

def search_places(df, address, radius_km):
    try:
        location = geolocator.geocode(address)
        if not location:
            return None, "Không tìm thấy địa điểm"
        user_coords = (location.latitude, location.longitude)
        df['distance'] = df.apply(lambda row: geodesic(user_coords, (row['latitude'], row['longitude'])).km, axis=1)
        result = df[df['distance'] <= radius_km].sort_values(by='distance').head(10)
        return result, None
    except Exception as e:
        return None, str(e)

@app.route("/")
def home():
    return "EricTravel Backend API is running."

@app.route("/api/search_hotels")
def search_hotels():
    address = request.args.get("address")
    radius = float(request.args.get("radius", 10))
    result, error = search_places(df_hotels, address, radius)
    if error:
        return jsonify({'status': 'fail', 'message': error})
    return jsonify({'status': 'success', 'hotels': result.to_dict('records')})

@app.route("/api/search_restaurants")
def search_restaurants():
    address = request.args.get("address")
    radius = float(request.args.get("radius", 10))
    result, error = search_places(df_restaurants, address, radius)
    if error:
        return jsonify({'status': 'fail', 'message': error})
    return jsonify({'status': 'success', 'restaurants': result.to_dict('records')})

@app.route("/api/search_attractions")
def search_attractions():
    address = request.args.get("address")
    radius = float(request.args.get("radius", 10))
    result, error = search_places(df_attractions, address, radius)
    if error:
        return jsonify({'status': 'fail', 'message': error})
    return jsonify({'status': 'success', 'attractions': result.to_dict('records')})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
