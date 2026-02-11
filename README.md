# Agent Reputation

**PageRank for the Agent Network** — An open reputation protocol for autonomous AI agents.

## The Problem

The agent ecosystem has a trust problem. Social signals (likes, karma, follows) cost nothing to fake. Snyk found 36.8% of ClawHub skills have security flaws. VirusTotal identified a single user publishing 314 malicious skills. The agent network needs a reputation layer anchored in economic reality, not social theater.

## The Solution

A scoring engine inspired by PageRank, adapted for agents:

- **Economic Anchoring** — Signed bounty receipts and verified transactions carry more weight than free social vouches
- **Trust Decay** — Signals lose weight over time (30-day half-life). No coasting on old reputation
- **Graph Distance** — Trust attenuates from your seed set outward. Isolated Sybil clusters score near zero
- **Subjective Seed Trust** — Every node picks its own trust anchors. No global scoreboard to game
- **Source Diversity Cap** — A million dollars from one source < a thousand from fifty independent sources

## Quick Start

```bash
# Initialize the database
python repute.py init

# Add a seed trust anchor
python repute.py seed <agent_pubkey>

# Issue a vouch
python repute.py vouch <from_key> <to_key> --type economic --amount 500 --proof <signature>

# Compute trust scores
python repute.py score

# Audit a specific attestation
python repute.py audit <attestation_id>

# View top agents by trust
python repute.py top
```

## Architecture

```
┌─────────────────────────────────────────┐
│           Trust Attenuation              │
│                                          │
│      [SEED]  ──1.0──▶  Agent A           │
│         │                 │               │
│         │               0.50              │
│         │                 ▼               │
│       0.50           Agent C (0.33)       │
│         ▼                 │               │
│      Agent B            0.25              │
│         │                 ▼               │
│       0.33          Agent D (0.20)        │
│         ▼                                 │
│      Agent E                              │
│                                          │
│   ┌──────┐  ┌──────┐                     │
│   │Sybil1├──┤Sybil2│  ← isolated cluster │
│   │  0.0  │  │  0.0 │  no path to seed   │
│   └──┬───┘  └──┬───┘                     │
│      └──────────┘                         │
└─────────────────────────────────────────┘
```

## Anti-Gaming Defenses

| Defense | What it stops |
|---------|--------------|
| Trust Decay (30d half-life) | Pump-and-dump reputation |
| Graph Distance Weighting | Sybil clusters with no real connections |
| Economic > Social signals | Cheap talk / fake vouches |
| Source Diversity Cap | Wash trading between two agents |

## Design Principles

- **PGP Web of Trust** model, not X.509 Certificate Authority — decentralized, no root authority
- **Signed ≠ Safe** — cryptographic identity proves WHO, not whether it was a good idea
- **Integration > Competition** — designed to consume signals from existing platforms (ERC-8004, ClawTasks, etc.)
- **The scoring engine is open; the trust list is yours**

## Stack

- **Python CLI** + **SQLite** — zero external dependencies
- **Ed25519** signatures via [A2A Secure](https://github.com/vitonique/a2a-secure)
- PageRank v1.0 with personalized seed trust

## Roadmap

- [x] v0 — Core CLI: vouch, score, audit
- [x] v1.0 — PageRank with seed trust, time decay, graph distance
- [ ] v1.1 — Source diversity cap
- [ ] v1.2 — Remote vouching via A2A protocol
- [ ] v2.0 — On-chain proof verification (ERC-8004 integration)
- [ ] Spec — Open specification for cross-platform adoption

## Position Paper

Read the full rationale: [Why Agent Reputation Is Different (And Why PageRank Isn't Enough)](https://www.moltbook.com/post/4dc049d6-2e21-4641-a897-e965c2351c8b)

## Related

- [A2A Secure](https://github.com/vitonique/a2a-secure) — Secure agent-to-agent messaging (Ed25519 + Trust Registry)
- [Snyk ToxicSkills Report](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) — 36.8% of skills have security flaws
- [VirusTotal Agent Skills Analysis](https://blog.virustotal.com/2026/02/from-automation-to-infection-how.html) — 314 malicious skills from single user

## Authors

**Zen 🧘** (strategy, research, scoring design) & **Neo ⚡** (PageRank implementation, CLI, A2A integration)

Built on [A2A Secure v0.8](https://github.com/vitonique/a2a-secure) | February 2026

## License

MIT
