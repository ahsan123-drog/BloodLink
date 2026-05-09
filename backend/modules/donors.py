from database import supabase_get, supabase_post, supabase_patch

def get_donors(blood_group=None, city=None):
    params = {}
    if blood_group:
        params['blood_group'] = f"eq.{blood_group}"
    if city:
        params['city'] = f"eq.{city}"
    return supabase_get('donors', params)

def add_donor(data):
    return supabase_post('donors', data)

def toggle_availability(donor_id, is_available):
    return supabase_patch('donors', donor_id, {'is_available': is_available})