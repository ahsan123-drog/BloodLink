from flask import Flask, request, jsonify
from flask_cors import CORS
from database import supabase_post, supabase_get, supabase_patch
import json

app = Flask(__name__)
CORS(app)

# ---------- Helper: Register user + donor profile ----------
def register_user_and_donor(data):
    # 1. Insert into users
    user_data = {
        "phone": data['phone'],
        "full_name": data['full_name'],
        "roles": ["DONOR"]
    }
    user_res = supabase_post('users', user_data)
    if not user_res:
        return None, "User insert failed"
    user_id = user_res[0]['id']
    
    # 2. Insert into donor_profiles
    donor_data = {
        "user_id": user_id,
        "blood_group": data['blood_group'],
        "dob": data['dob'],
        "city": data['city'],
        "weight_kg": data.get('weight_kg'),
        "location": None,
        "verification_status": "UNVERIFIED",
        "availability_status": "ACTIVE"
    }
    if data.get('latitude') and data.get('longitude'):
        donor_data["location"] = f"POINT({data['longitude']} {data['latitude']})"
    donor_res = supabase_post('donor_profiles', donor_data)
    if not donor_res:
        return None, "Donor profile insert failed"
    
    return user_id, None

# ---------- Donor Registration ----------
@app.route('/api/donors', methods=['POST'])
def register_donor():
    data = request.json
    required = ['phone', 'full_name', 'blood_group', 'dob', 'city']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    user_id, error = register_user_and_donor(data)
    if error:
        return jsonify({"error": error}), 500
    
    return jsonify({"message": "Donor registered", "user_id": user_id}), 201

# ---------- Search Donors ----------
@app.route('/api/donors', methods=['GET'])
def search_donors():
    blood_group = request.args.get('blood_group')
    city = request.args.get('city')
    
    # Fetch donor_profiles with optional filters
    filters = {}
    if blood_group:
        filters['blood_group'] = f"eq.{blood_group}"
    if city:
        filters['city'] = f"eq.{city}"
    
    donor_res = supabase_get('donor_profiles', filters)
    if not donor_res:
        return jsonify([])
    
    # Enrich with user details
    result = []
    for donor in donor_res:
        user_res = supabase_get('users', {'id': f"eq.{donor['user_id']}"})
        if user_res:
            user = user_res[0]
            result.append({
                "user_id": donor['user_id'],
                "name": user['full_name'],
                "blood_group": donor['blood_group'],
                "city": donor['city'],
                "phone": user['phone'],
                "is_available": donor['availability_status'] == 'ACTIVE'
            })
    return jsonify(result)

# ---------- Blood Request ----------
@app.route('/api/requests', methods=['POST'])
def post_blood_request():
    data = request.json
    required = ['requester_id', 'blood_group', 'hospital_name', 'city', 'contact_phone']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    request_data = {
        "requester_id": data['requester_id'],
        "blood_group": data['blood_group'],
        "units_needed": data.get('units_needed', 1),
        "hospital_name": data['hospital_name'],
        "city": data['city'],
        "urgency": data.get('urgency', 'NORMAL'),
        "status": "OPEN",
        "is_verified": False
    }
    if data.get('latitude') and data.get('longitude'):
        request_data["location"] = f"POINT({data['longitude']} {data['latitude']})"
    
    res = supabase_post('blood_requests', request_data)
    if not res:
        return jsonify({"error": "Failed to post request"}), 500
    return jsonify({"message": "Request posted", "request_id": res[0]['id']}), 201

@app.route('/api/requests', methods=['GET'])
def get_blood_requests():
    res = supabase_get('blood_requests', {'order': 'urgency.desc,created_at.desc'})
    for req in res:
        user_res = supabase_get('users', {'id': f"eq.{req['requester_id']}"})
        req['requester_name'] = user_res[0]['full_name'] if user_res else 'Unknown'
    return jsonify(res)

# ---------- Chat ----------
@app.route('/api/chat/send', methods=['POST'])
def send_chat_message():
    data = request.json
    if not all(k in data for k in ('donor_id', 'requester_name', 'message')):
        return jsonify({"error": "Missing fields"}), 400
    msg_data = {
        "donor_id": data['donor_id'],
        "requester_name": data['requester_name'],
        "message": data['message']
    }
    supabase_post('chat_messages', msg_data)
    return jsonify({"message": "Sent"}), 201

@app.route('/api/chat/messages/<donor_id>', methods=['GET'])
def get_chat_messages(donor_id):
    res = supabase_get('chat_messages', {'donor_id': f"eq.{donor_id}", 'order': 'created_at.asc'})
    return jsonify(res)

# ---------- Donor Availability Toggle ----------
@app.route('/api/donors/<user_id>/availability', methods=['PATCH'])
def toggle_availability(user_id):
    data = request.json
    new_status = data.get('availability_status')
    if new_status not in ['ACTIVE', 'UNAVAILABLE']:
        return jsonify({"error": "Invalid status"}), 400
    
    donor_res = supabase_get('donor_profiles', {'user_id': f"eq.{user_id}"})
    if not donor_res:
        return jsonify({"error": "Donor not found"}), 404
    donor_id = donor_res[0]['id']
    
    res = supabase_patch('donor_profiles', donor_id, {'availability_status': new_status})
    if not res:
        return jsonify({"error": "Update failed"}), 500
    return jsonify({"message": "Availability updated"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)