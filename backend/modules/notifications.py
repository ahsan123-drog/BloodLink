from database import supabase_post

def send_notification(donor_id, message):
    return supabase_post('notifications', {
        'donor_id': donor_id,
        'message': message,
        'is_sent': True
    })