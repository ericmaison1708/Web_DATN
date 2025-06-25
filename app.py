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

# Đường dẫn tới thư mục chứa CSV
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def search_places_chunked(filename, address, radius_km, top_n=10, chunksize=10000):
    """
    Đọc CSV theo chunks, tính khoảng cách đến address, 
    giữ lại những row trong radius_km, rồi sort & cắt top_n.
    """
    loc = geolocator.geocode(address)
    if not loc:
        return None, "Không tìm thấy địa điểm"
    user_coord = (loc.latitude, loc.longitude)

    matches = []
    csv_path = os.path.join(DATA_DIR, filename)

    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        # bỏ các dòng thiếu tọa độ
        chunk = chunk.dropna(subset=['latitude', 'longitude'])
        # tính distance
        chunk['distance'] = chunk.apply(
            lambda r: geodesic(user_coord, (r['latitude'], r['longitude'])).km,
            axis=1
        )
        # lọc theo bán kính
        within = chunk[chunk['distance'] <= radius_km]
        if not within.empty:
            matches.extend(within.to_dict('records'))

    # sort theo khoảng cách
    matches.sort(key=lambda x: x['distance'])
    # trả về tối đa top_n
    return matches[:top_n], None

@app.route('/')
def home():
    return "EricTravel Backend API is running."

@app.route('/api/search_hotels')
def api_search_hotels():
    address = request.args.get('address', '')
    radius = float(request.args.get('radius', 10))
    results, error = search_places_chunked('hotels.csv', address, radius)
    if error:
        return jsonify({ 'status': 'fail', 'message': error })
    return jsonify({ 'status': 'success', 'hotels': results })

@app.route('/api/search_restaurants')
def api_search_restaurants():
    address = request.args.get('address', '')
    radius = float(request.args.get('radius', 10))
    results, error = search_places_chunked('restaurants.csv', address, radius)
    if error:
        return jsonify({ 'status': 'fail', 'message': error })
    return jsonify({ 'status': 'success', 'restaurants': results })

@app.route('/api/search_attractions')
def api_search_attractions():
    address = request.args.get('address', '')
    radius = float(request.args.get('radius', 10))
    results, error = search_places_chunked('attractions.csv', address, radius)
    if error:
        return jsonify({ 'status': 'fail', 'message': error })
    return jsonify({ 'status': 'success', 'attractions': results })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
