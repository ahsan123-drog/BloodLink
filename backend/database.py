import requests
import json
from config import SUPABASE_URL, SUPABASE_KEY

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def supabase_get(table, params=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"GET {url} -> Status: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error response: {response.text}")
            return []
    except Exception as e:
        print(f"Exception in GET: {e}")
        return []

def supabase_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    try:
        print(f"POST to: {url}")
        print(f"Data: {data}")
        response = requests.post(url, headers=headers, json=data)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 201:
            if response.text:
                return response.json()
            else:
                return [{"id": "saved"}]
        else:
            return None
    except Exception as e:
        print(f"Exception in POST: {e}")
        return None

def supabase_patch(table, id, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id}"
    try:
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Exception in PATCH: {e}")
        return None

print("✅ Supabase connected!")