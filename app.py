from flask import Flask, request, jsonify
from flask_cors import CORS
from opencage.geocoder import OpenCageGeocode
from geopy.distance import geodesic
import pandas as pd
import gdown
import os

app = Flask(__name__)
CORS(app)

# Khởi tạo OpenCage Geocoder
OPENCAGE_API_KEY = "71e47c02d8bc430fb418c4a9046bdb73"
geocoder = OpenCageGeocode(OPENCAGE_API_KEY)

# Đường dẫn tới thư mục chứa CSV
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def download_if_not_exists_from_drive(file_id, local_path):
    if not os.path.exists(local_path):
        print(f"Downloading {local_path} from Google Drive ...")
        gdown.download(id=file_id, output=local_path, quiet=False)

# ✅ Thay các ID này bằng ID thực từ Google Drive của bạn
HOTEL_CSV_URL = 'https://drive.google.com/uc?export=download&id=1BpuhPSRhz6HQVHL4NEhj59KlpYPad-gY'
RESTAURANT_CSV_URL = 'https://drive.google.com/uc?export=download&id=1NJe9IDuwCEqdX7IcJVGq0b81b-tYKYwg'
ATTRACTION_CSV_URL = 'https://drive.google.com/file/d/1BUbRRCKJKjSwlPbbAC1c2kJbhn_8rth5/view?usp=sharing'  

# ✅ Tải cả 3 file nếu chưa tồn tại
download_if_not_exists_from_drive('1BpuhPSRhz6HQVHL4NEhj59KlpYPad-gY', os.path.join(DATA_DIR, 'hotels.csv'))
download_if_not_exists_from_drive('1NJe9IDuwCEqdX7IcJVGq0b81b-tYKYwg', os.path.join(DATA_DIR, 'restaurants.csv'))
download_if_not_exists_from_drive('1BUbRRCKJKjSwlPbbAC1c2kJbhn_8rth5', os.path.join(DATA_DIR, 'attractions.csv'))

def search_places_chunked(filename, address, radius_km, top_n=10, chunksize=10000):
    """
    Đọc CSV theo chunks, tính khoảng cách đến address, 
    giữ lại những row trong radius_km, rồi sort & cắt top_n.
    """
    geo_result = geocoder.geocode(address)
    if not geo_result:
        return None, "Không tìm thấy địa điểm"
    user_coord = (geo_result[0]['geometry']['lat'], geo_result[0]['geometry']['lng'])

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
            # 🔧 FIX: Thay NaN trong các cột như Price thành None (JSON hợp lệ)
            within = within.where(pd.notnull(within), None)

            # chuyển thành dict để trả JSON
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
