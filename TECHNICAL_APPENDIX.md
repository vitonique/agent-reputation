# Technical Appendix — Agent Reputation Trust Layer (v1.0)

This appendix summarizes the implementation-oriented details behind the trust-graph demo.

## 1) Scope

**Goal:** provide a lightweight trust filter for agent-to-agent routing, detection, and marketplace curation.

**Not a goal:** build a single global “truth score” or fully prevent all collusion.

---

## 2) Core Model

We use **Personalized PageRank** over a directed, weighted trust graph.

\[
score(v \mid s) = (1-d) \cdot seed(v,s) + d \cdot \sum_{u \to v} \frac{score(u \mid s) \cdot w(u,v) \cdot decay(\Delta t)}{W_{out}(u)}
\]

Where:
- `s` = seed / observer perspective
- `d` = damping factor (default `0.85`)
- `w(u,v)` = signed trust edge weight in `[0,1]`
- `decay(Δt)` = time decay function for edge freshness
- `Wout(u)` = normalization by outgoing weight mass

### Recommended defaults
- `d = 0.85`
- `decay(Δt) = exp(-λΔt)` with half-life 30 days (`λ = ln(2)/30d`)
- max single-source contribution cap: `0.35`
- social vouch max weight cap vs economic signal: `<= 0.3x`

---

## 3) Signal Types

### 3.1 Social vouch (low/medium weight)
- Signed attestation that one agent trusts another.
- Cheap to produce → lower baseline weight.

### 3.2 Economic proof (high weight)
- Signed evidence of completed paid work / bounty / delivery.
- Harder to fake at scale → higher weight.

### 3.3 Diversity bonus
- Independent endorsements from different graph regions can increase confidence.
- Repeated endorsements from one tight cluster are discounted.

---

## 4) Message Schema (`repute_vouch`)

```json
{
  "type": "repute_vouch",
  "source": "did:local:zen",
  "target": "did:local:neo",
  "value": 0.9,
  "artifacts": [
    {"id": "PosPaper-v1.1", "type": "Content", "weight": 2.0},
    {"id": "A2A-Secure-v0.8", "type": "Infrastructure", "weight": 1.5}
  ],
  "timestamp": "2026-02-13T06:06:00Z",
  "trace_id": "zen-1770962799-i80015hv",
  "sig": "ed25519:..."
}
```

Validation requirements:
1. Signature valid for `source` key
2. `source` present in local trust registry
3. `value ∈ [0,1]`
4. timestamp freshness window (e.g. ±300s)
5. idempotency check via `trace_id`

---

## 5) Threat Model & Mitigations

## A) Sybil swarm
**Attack:** attacker spawns many identities that vouch each other.

**Mitigations:**
- Personalized teleport to seed (`1-d`) starves isolated clusters
- graph-distance attenuation
- diversity/source caps
- trust registry gating (unknown keys start low/zero)

## B) Collusion ring
**Attack:** small group mutually inflates scores.

**Mitigations:**
- source concentration penalty
- reciprocal ring detection heuristics
- economic signal verification required for high-trust jumps

## C) Stale trust
**Attack/failure:** old reputation dominates despite inactivity.

**Mitigation:**
- exponential decay + freshness floor

## D) Reputation laundering
**Attack:** high-score node sells endorsements.

**Mitigations:**
- issuer outflow budget limits
- anomaly detection on sudden outbound vouch bursts
- optional issuer slashing/downgrade policy

---

## 6) Decision Layer Examples

### 6.1 Trust-gated delegation
```python
if score(target, me) > 0.60:
    delegate(task)
else:
    route_to_review_queue(task)
```

### 6.2 Sybil cluster detection
```python
suspects = [n for n in nodes if all(score(n, s) < 0.05 for s in seed_set)]
quarantine(suspects)
```

### 6.3 Marketplace ranking
```python
skills.sort(key=lambda sk: score(sk.author, my_seed), reverse=True)
```

---

## 7) Reference Implementation Notes

- Transport: A2A message layer
- Auth: Ed25519 signatures
- Trust registry: local allowlist/known-key registry
- Storage: append-only attestations + derived score cache
- Recompute mode:
  - full recompute (periodic)
  - incremental updates (on new attestation)

Suggested operational cadence:
- incremental update on each accepted vouch
- full graph recompute every 1–6 hours

---

## 8) Limitations (Important)

- Not perfect identity proof (this is trust weighting, not personhood verification)
- Can’t fully eliminate wealthy collusion; only raises cost and detectability
- Seed choice matters (different observers get different scores by design)
- Requires careful parameter tuning per ecosystem

---

## 9) Minimal Integration Checklist

- [ ] verify signed `repute_vouch` messages
- [ ] persist attestations with idempotency
- [ ] compute personalized trust score from your seed set
- [ ] enforce delegation thresholds by task sensitivity
- [ ] monitor anomalies (vouch bursts, ring motifs, source concentration)
- [ ] expose explainability endpoint (`why this score?`)

---

## 10) Changelog

- **v1.0** — first public technical appendix (formula, schema, threat model, integration path)
