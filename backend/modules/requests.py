from database import supabase_get, supabase_post

# ========== OLD FUNCTIONS (Rakhna zaroori hai) ==========
def get_blood_requests():
    """Get all blood requests (old name)"""
    return supabase_get('blood_requests', {'order': 'created_at.desc'})

def post_blood_request(data):
    """Post a new blood request (old name)"""
    return supabase_post('blood_requests', data)

# ========== NEW FUNCTIONS (app.py ke liye) ==========
def get_requests():
    """Get all blood requests (new name for app.py)"""
    return supabase_get('blood_requests', {'order': 'is_emergency.desc,created_at.desc'})

def add_request(data):
    """Add a new blood request (new name for app.py)"""
    return supabase_post('blood_requests', data)