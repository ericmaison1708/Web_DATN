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

# Thư mục dữ liệu CSV
data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Hàm tìm kiếm nâng cao: đọc theo chunks để tiết kiệm RAM
def search_places(filename, address, radius_km):
    try:
        location = geolocator.geocode(address)
        if not location:
            return None, "Không tìm thấy địa điểm"
        user_coords = (location.latitude, location.longitude)
        matches = []
        # Đọc CSV theo chunksize (10k dòng/ lần)
        for chunk in pd.read_csv(os.path.join(data_dir, filename), chunksize=10000):
            # Loại bỏ dòng thiếu tọa độ
            chunk = chunk.dropna(subset=['latitude', 'longitude'])
            # Tính khoảng cách
            chunk['distance'] = chunk.apply(
                lambda row: geodesic(user_coords, (row['latitude'], row['longitude'])).km,
                axis=1
            )
            # Lọc trong bán kính
            within = chunk[chunk['distance'] <= radius_km]
            if not within.empty:
                matches.extend(within.to_dict('records'))
        # Sắp xếp và lấy tối đa 10 kết quả gần nhất
        matches.sort(key=lambda x: x['distance'])
        return matches[:10], None
    except Exception as e:
        return None, str(e)

@app.route("/")
def home():
    return "EricTravel Backend API is running."

@app.route("/api/search_hotels")
def search_hotels():
    address = request.args.get("address")
    radius = float(request.args.get("radius", 10))
    result, error = search_places('hotels.csv', address, radius)
    if error:
        return jsonify({'status': 'fail', 'message': error})
    return jsonify({'status': 'success', 'hotels': result})

@app.route("/api/search_restaurants")
def search_restaurants():
    address = request.args.get("address")
    radius = float(request.args.get("radius", 10))
    result, error = search_places('restaurants.csv', address, radius)
    if error:
        return jsonify({'status': 'fail', 'message': error})
    return jsonify({'status': 'success', 'restaurants': result})

@app.route("/api/search_attractions")
def search_attractions():
    address = request.args.get("address")
    radius = float(request.args.get("radius", 10))
    result, error = search_places('attractions.csv', address, radius)
    if error:
        return jsonify({'status': 'fail', 'message': error})
    return jsonify({'status': 'success', 'attractions': result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Không preload toàn bộ CSV, giảm bộ nhớ
    app.run(host="0.0.0.0", port=port)
