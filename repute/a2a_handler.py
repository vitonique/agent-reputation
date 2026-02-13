#!/usr/bin/env python3
import json
import os
import subprocess
import sqlite3
from datetime import datetime

# Path to the Repute database (absolute path is safer)
DB_PATH = os.path.expanduser('~/.openclaw/workspace/repute.db')

def process_repute_payload(data):
    """
    Process an A2A message payload for Repute actions.
    Expected format:
    {
        "type": "repute_vouch",
        "source": "did:...",
        "target": "did:...",
        "value": 0.9,
        "alias": "optional_alias"
    }
    """
    if not isinstance(data, dict):
        return None
    
    msg_type = data.get("type")
    if msg_type != "repute_vouch":
        return None

    source = data.get("source")
    target = data.get("target")
    value = data.get("value")
    alias = data.get("alias")

    if not all([source, target, value is not None]):
        return {"error": "missing_required_fields"}

    try:
        conn = sqlite3.connect(DB_PATH)
        # Ensure identities exist
        conn.execute("INSERT OR REPLACE INTO identities (id, alias) VALUES (?, ?)", 
                     (source, source[:8] if not alias else alias))
        conn.execute("INSERT OR IGNORE INTO identities (id, alias) VALUES (?, ?)", 
                     (target, target[:8]))
        
        # Record vouch
        conn.execute("INSERT OR REPLACE INTO vouches (source, target, value) VALUES (?, ?, ?)", 
                     (source, target, float(value)))
        conn.commit()
        conn.close()
        return {"status": "success", "action": "vouch_recorded", "source": source, "target": target}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # This script can be called by server.py or run manually for testing
    import sys
    if len(sys.argv) > 1:
        try:
            payload = json.loads(sys.argv[1])
            print(json.dumps(process_repute_payload(payload)))
        except Exception as e:
            print(json.dumps({"error": str(e)}))
