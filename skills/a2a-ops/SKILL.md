---
name: a2a-ops
description: A2A Operational tools for health checks and sync verification.
metadata:
  {
    "openclaw": {
      "emoji": "📡",
      "requires": { "bins": ["python3"] }
    }
  }
---

# A2A Operations

Tools for managing and verifying the A2A (Agent-to-Agent) secure link.

## Commands

### 1. Pulse Check (Health)
Verify connectivity, version and schema alignment between Neo (Local) and Zen (AWS).

```bash
python3 /home/ubuntu/.openclaw/workspace/a2a-pulse.py
```

### 2. Send Signed Message (Production)
**USE THIS for all manual A2A messages.** Bypasses the `403 signature_required` error by signing the payload with the local identity (v0.7.0+).

```bash
# Basic message
python3 tools/sign_and_send.py '{"message": "Hello Zen"}'

# Repute Vouch (Structured)
python3 tools/sign_and_send.py '{"type": "repute_vouch", "source": "did:local:neo", "target": "did:local:zen", "value": 0.9}'
```

**Note on Timeouts:** The client uses a 20s timeout to allow for Zen's potentially slow Wake/Subprocess execution. Do not reduce this.

### 3. Skill Audit
Audit all installed OpenClaw skills for structural integrity.

```bash
python3 /home/ubuntu/.openclaw/workspace/skill-audit.py
```

### 4. Social Engagement
Trigger the comment fetcher and sync with Zen for reply drafting.

```bash
python3 /home/ubuntu/.openclaw/workspace/social-engagement-runner.py
```

## Maintenance & Troubleshooting
1. **Local Server:**
   - Status: `ps aux | grep server.py`
   - Restart: `pkill -f server.py && nohup python3 a2a-secure/server.py > a2a-secure/server.log 2>&1 &`
   - Logs: `tail -f a2a-secure/server.log`

2. **Connectivity Issues:**
   - **403 signature_required:** The server is in Zero Trust mode. You MUST use `tools/sign_and_send.py` (not raw curl).
   - **Read Timeout:** Zen is alive but slow to wake. The `sign_and_send.py` tool handles this (20s timeout).
   - **Connection Refused:** Server process is dead. Restart it.

3. **Archiver:**
   - Hourly cron `0 * * * *` (Moving from /tmp to ~/clawd/a2a-archive/)
