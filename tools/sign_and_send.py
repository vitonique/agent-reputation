#!/usr/bin/env python3
"""A2A Sign-and-Send Utility for Repute Vouching ⚡

Uses local identity.py to sign the payload and send it to Zen.
Bypasses the 403 signature_required error.
"""

import sys
import json
import base64
import time
import requests
import uuid
from identity import get_or_create_hot_key, sign_message_dict

ZEN_URL = "http://35.158.138.126:8080"

def send_signed(payload_dict):
    # 1. Add required envelope fields
    payload_dict["ts"] = time.time()
    if "trace_id" not in payload_dict:
        payload_dict["trace_id"] = f"neo-{int(time.time())}-{str(uuid.uuid4())[:8]}"
    
    # 2. Sign
    hk = get_or_create_hot_key()
    pub_b64 = base64.b64encode(hk.pub_raw32()).decode("ascii")
    
    payload_dict["identity"] = {
        "hot_pub_b64": pub_b64
    }
    
    # Sign the dictionary (canonicalized)
    sig = sign_message_dict(hk, payload_dict)
    payload_dict["sig"] = sig
    
    print(f"⚡ Sending signed payload to {ZEN_URL}...")
    print(f"   Trace ID: {payload_dict['trace_id']}")
    print(f"   Pub Key: {pub_b64[:10]}...")
    
    try:
        # Increased timeout to 20s to handle potential Wake subprocess delays on Zen
        resp = requests.post(ZEN_URL, json=payload_dict, timeout=20)
        print(f"✅ Response ({resp.status_code}):")
        print(json.dumps(resp.json(), indent=2))
        return resp.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/sign_and_send.py '{\"message\": \"hello\"}'")
        sys.exit(1)
        
    raw_payload = sys.argv[1]
    try:
        payload = json.loads(raw_payload)
        send_signed(payload)
    except json.JSONDecodeError:
        print("Error: Invalid JSON string")
