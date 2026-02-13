#!/usr/bin/env python3
import argparse
import sys
import sqlite3
from datetime import datetime

DB_PATH = 'repute.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    with open('repute/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("✅ Database initialized.")

def ensure_identity(conn, did, alias=None):
    if alias:
        conn.execute("INSERT OR REPLACE INTO identities (id, alias) VALUES (?, ?)", (did, alias))
    else:
        conn.execute("INSERT OR IGNORE INTO identities (id, alias) VALUES (?, ?)", (did, did[:8]))

def cmd_vouch(args):
    conn = get_conn()
    try:
        ensure_identity(conn, args.source)
        ensure_identity(conn, args.target)
        
        conn.execute("INSERT OR REPLACE INTO vouches (source, target, value) VALUES (?, ?, ?)", 
                     (args.source, args.target, args.value))
        conn.commit()
        print(f"✅ Vouch recorded: {args.source} -> {args.target} (val={args.value})")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def compute_pagerank(seed_id=None, iterations=20, damping=0.85, time_decay=False):
    conn = get_conn()
    identities = [row['id'] for row in conn.execute("SELECT id FROM identities")]
    if not identities:
        return {}
    
    n = len(identities)
    scores = {id: 1.0/n for id in identities}
    
    # Get all vouches
    vouches = []
    now = datetime.now()
    for row in conn.execute("SELECT source, target, value, timestamp FROM vouches"):
        val = row['value']
        if time_decay:
            ts = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            days_old = (now - ts).days
            # Half-life of 30 days
            decay = 0.5 ** (days_old / 30.0)
            val *= decay
        vouches.append((row['source'], row['target'], val))
    
    # SV Signal: Boost nodes with high output artifacts
    # For MVP, we look at artifacts table
    sv_boost = {id: 1.0 for id in identities}
    try:
        for row in conn.execute("SELECT owner_id, weight FROM artifacts"):
            if row['owner_id'] in sv_boost:
                sv_boost[row['owner_id']] += row['weight']
    except sqlite3.OperationalError:
        pass # artifacts table might not exist yet
    
    out_degrees = {id: 0.0 for id in identities}
    for src, tgt, val in vouches:
        if src in out_degrees:
            out_degrees[src] += val
        
    for _ in range(iterations):
        if seed_id and seed_id in identities:
            new_scores = {id: 0.0 for id in identities}
            jump_val = (1.0 - damping)
            new_scores[seed_id] = jump_val
        else:
            new_scores = {id: (1.0 - damping) / n for id in identities}
            
        for src, tgt, val in vouches:
            if src in out_degrees and out_degrees[src] > 0:
                # SV weight integration: high SV nodes contribute more weight to the total pool
                # This is a simple implementation where SV acts as a multiplier on the incoming score
                new_scores[tgt] += damping * (scores[src] * sv_boost.get(src, 1.0)) * (val / out_degrees[src])
        
        sink_sum = sum(scores[id] for id in identities if out_degrees.get(id, 0) == 0)
        for id in identities:
            if seed_id and seed_id in identities:
                if id == seed_id:
                    new_scores[id] += damping * sink_sum
            else:
                new_scores[id] += damping * sink_sum / n
            
        norm = sum(new_scores.values())
        if norm > 0:
            scores = {id: s/norm for id, s in new_scores.items()}
        else:
            scores = new_scores
        
    conn.close()
    return scores

def cmd_score(args):
    scores = compute_pagerank(seed_id=args.seed, time_decay=args.decay)
    score = scores.get(args.target, 0.0)
    label = []
    if args.seed: label.append(f"Seed: {args.seed}")
    if args.decay: label.append("TimeDecay: ON")
    label_str = f" ({', '.join(label)})" if label else ""
    print(f"🏅 Repute Score{label_str} for {args.target}: {score:.6f}")

def cmd_audit(args):
    conn = get_conn()
    print("\n--- Identities ---")
    for row in conn.execute("SELECT * FROM identities"):
        print(f"{row['id']} ({row['alias']})")
    
    print("\n--- Vouches ---")
    for row in conn.execute("SELECT * FROM vouches"):
        print(f"{row['source']} -> {row['target']} : {row['value']} ({row['timestamp']})")
    conn.close()

def cmd_top(args):
    scores = compute_pagerank(seed_id=args.seed, time_decay=args.decay)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    label = []
    if args.seed: label.append(f"Seed: {args.seed}")
    if args.decay: label.append("TimeDecay: ON")
    label_str = f" ({', '.join(label)})" if label else ""
    
    print(f"\n🏆 Top Identities{label_str}:")
    for i, (id, score) in enumerate(sorted_scores[:args.limit], 1):
        print(f"{i}. {id}: {score:.6f}")

def main():
    parser = argparse.ArgumentParser(description="Repute MVP CLI ⚡")
    subparsers = parser.add_subparsers()

    # init
    p_init = subparsers.add_parser('init', help='Initialize DB')
    p_init.set_defaults(func=lambda args: init_db())

    # vouch
    p_vouch = subparsers.add_parser('vouch', help='Vouch for an identity')
    p_vouch.add_argument('source', help='Source DID')
    p_vouch.add_argument('target', help='Target DID')
    p_vouch.add_argument('value', type=float, help='Value (0.0-1.0)')
    p_vouch.set_defaults(func=cmd_vouch)

    # score
    p_score = subparsers.add_parser('score', help='Get score')
    p_score.add_argument('target', help='Target DID')
    p_score.add_argument('--seed', help='Seed DID for Personalized PageRank')
    p_score.add_argument('--decay', action='store_true', help='Apply time decay to vouches')
    p_score.set_defaults(func=cmd_score)

    # top
    p_top = subparsers.add_parser('top', help='Show top identities')
    p_top.add_argument('--limit', type=int, default=10, help='Number of results')
    p_top.add_argument('--seed', help='Seed DID for Personalized PageRank')
    p_top.add_argument('--decay', action='store_true', help='Apply time decay to vouches')
    p_top.set_defaults(func=cmd_top)

    # audit
    p_audit = subparsers.add_parser('audit', help='Dump DB state')
    p_audit.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
