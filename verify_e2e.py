"""
Project Drishti — End-to-End Verification Harness
File: verify_e2e.py

Answers the question "does the product actually work?" with evidence, by
exercising the real chain a judge will see:

    WebSocket client connects   (stands in for the React dashboard)
        -> POST /api/v1/transactions/   (stands in for the bank feed)
            -> trigger service fires
                -> ML engine predicts
                    -> broadcast
                        -> client receives and we ASSERT on the contents

Every check prints PASS or FAIL with the value it saw. A green run is the only
acceptable state before presenting; a red one names the exact broken link, so
nobody has to guess which of the three services is at fault.

Run:  python verify_e2e.py          (backend must already be running on :8000)
"""

import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

BASE = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/live_alerts"
IST = timezone(timedelta(hours=5, minutes=30))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_results = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    _results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -> {detail}" if detail else ""))
    return ok


def section(title: str):
    print(f"\n{'=' * 74}\n  {title}\n{'=' * 74}")


def http_post(path: str, payload: dict, timeout=180):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode() or "{}")


def http_get(path: str, timeout=30):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return r.status, r.read().decode()


def main():
    print("\n" + "#" * 74)
    print("#  PROJECT DRISHTI — END-TO-END VERIFICATION")
    print("#" * 74)

    # ── 1. Backend reachable ────────────────────────────────────────────────
    section("1. BACKEND REACHABILITY")
    try:
        status, _ = http_get("/docs")
        check("Backend is up (GET /docs)", status == 200, f"HTTP {status}")
    except Exception as e:
        check("Backend is up (GET /docs)", False, str(e))
        print("\n  Backend is not running. Start it with:")
        print("    cd backend && python -m uvicorn app.main:app --port 8000")
        summarize()
        return

    # ── 2. WebSocket client connects BEFORE the transaction ────────────────
    section("2. WEBSOCKET SUBSCRIPTION (simulating the dashboard)")
    try:
        from websockets.sync.client import connect
    except ImportError:
        check("`websockets` library available", False, "pip install websockets")
        summarize()
        return

    try:
        ws = connect(WS_URL, open_timeout=15)
        check("Dashboard WebSocket connected", True, WS_URL)
    except Exception as e:
        check("Dashboard WebSocket connected", False, f"{type(e).__name__}: {e}")
        summarize()
        return

    # ── 3. Fire the transaction the bank feed would send ───────────────────
    section("3. TRANSACTION INGESTION -> ML TRIGGER")
    tx_id = f"E2E-{int(time.time())}"
    tx = {
        "tx_id": tx_id,
        "sender_id": "ACC-VICTIM-01",
        "receiver_id": "ACC-MULE-MASTER",
        "amount": 125000.00,
        "account_type": "Mule",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "last_known_lat": 28.6139,
        "last_known_lon": 77.2090,
    }
    t0 = time.time()
    try:
        status, body = http_post("/api/v1/transactions/", tx)
        latency = time.time() - t0
        check("POST /api/v1/transactions/ accepted", status in (200, 201), f"HTTP {status}")
        check("Backend reports the ML trigger fired",
              bool(body.get("alert_triggered")), json.dumps(body))
        check("Alert generated in under 5 s (interception budget)",
              latency < 5.0, f"{latency:.2f}s")
    except urllib.error.HTTPError as e:
        check("POST /api/v1/transactions/ accepted", False,
              f"HTTP {e.code}: {e.read().decode()[:200]}")
        ws.close()
        summarize()
        return
    except Exception as e:
        check("POST /api/v1/transactions/ accepted", False, f"{type(e).__name__}: {e}")
        ws.close()
        summarize()
        return

    # ── 4. Did the alert actually reach the dashboard? ─────────────────────
    section("4. ALERT DELIVERY OVER WEBSOCKET")
    alert = None
    try:
        raw = ws.recv(timeout=45)
        alert = json.loads(raw)
        check("Dashboard received a broadcast alert", True, f"{len(raw)} bytes")
    except Exception as e:
        check("Dashboard received a broadcast alert", False, f"{type(e).__name__}: {e}")
    finally:
        try:
            ws.close()
        except Exception:
            pass

    if not alert:
        summarize()
        return

    # ── 5. Is the payload a REAL prediction, and is it coherent? ───────────
    section("5. PAYLOAD CORRECTNESS (the part that decides if we can present)")

    check("Not serving the degraded fallback",
          alert.get("degraded") is False,
          f"degraded={alert.get('degraded')} "
          f"reason={alert.get('degraded_reason', '-')}")
    check("Ranker is the trained LambdaMART model",
          alert.get("model_used") == "LambdaMART",
          f"model_used={alert.get('model_used')}")
    check("Case ID traces back to the transaction",
          tx_id in str(alert.get("case_id", "")),
          f"case_id={alert.get('case_id')}")

    atms = alert.get("top_5_atms", [])
    check("Exactly 5 ATMs returned", len(atms) == 5, f"got {len(atms)}")
    check("Candidate pool was non-trivial",
          alert.get("total_candidates_evaluated", 0) >= 20,
          f"{alert.get('total_candidates_evaluated')} reachable cash points")

    if atms:
        # Every ATM must sit inside the interception radius. A candidate the
        # patrol cannot physically reach in the window is noise on the map.
        worst = max(a.get("travel_time_mins", 999) for a in atms)
        check("All 5 ATMs are reachable within the 45-min budget",
              worst <= 45, f"furthest = {worst} min")

        # THE ORIGINAL BUG: rank #1 was 40.7 min away while rank #4 was 23.0 min.
        # The model must not put a far ATM top unless it earns it on other
        # evidence, so we assert the top pick is not the worst of the five.
        top_travel = atms[0].get("travel_time_mins", 999)
        check("Rank #1 is not the furthest of the five (geography respected)",
              top_travel < worst or len(atms) == 1,
              f"rank#1 = {top_travel} min, furthest = {worst} min")

        probs = [a.get("confidence_score", 0) for a in atms]
        check("Confidences are valid probabilities in [0,1]",
              all(0.0 <= p <= 1.0 for p in probs),
              f"{[round(p, 3) for p in probs]}")
        check("Confidences are monotonically non-increasing by rank",
              all(probs[i] >= probs[i + 1] - 1e-9 for i in range(len(probs) - 1)),
              f"{[round(p, 3) for p in probs]}")
        check("Top pick has actionable confidence (>10%)",
              probs[0] > 0.10, f"rank#1 = {probs[0]:.1%}")
        check("Top-5 captures the majority of probability mass",
              alert.get("top5_probability_mass", 0) > 0.5,
              f"{alert.get('top5_probability_mass', 0):.1%}")

        check("Every ATM has real GPS coordinates for the map",
              all(a.get("latitude") and a.get("longitude") for a in atms))
        check("Every ATM carries a dispatch explanation",
              all(len(str(a.get("explanation", ""))) > 25 for a in atms))
        # Word-boundary anchored: a naive substring test matches "40 prior" and
        # "10 linked", which are perfectly good evidence.
        zero_evidence = re.compile(r"(?<!\d)0 (prior|linked|confirmed|recorded)")
        offenders = [a["rank"] for a in atms
                     if zero_evidence.search(str(a.get("explanation", "")))]
        check("No explanation cites zero-valued evidence",
              not offenders, f"offending ranks: {offenders}" if offenders else "")

    # ── 6. The WHEN engine ────────────────────────────────────────────────
    section("6. WHEN ENGINE (interception window)")
    # Defensive: a degraded payload may carry time_window as a bare string.
    tw = alert.get("time_window", {})
    if not isinstance(tw, dict):
        check("time_window is a structured object", False, f"got {type(tw).__name__}: {tw!r}")
        tw = {}
    check("Window came from a trained survival model",
          tw.get("model_source") in ("CoxProportionalHazards", "KaplanMeier"),
          f"source={tw.get('model_source')}")
    check("Window is case-specific (Cox, not a population constant)",
          tw.get("model_source") == "CoxProportionalHazards",
          f"source={tw.get('model_source')}")
    check("Window has a sane width (5-120 min)",
          5 <= tw.get("window_minutes", 0) <= 120,
          f"{tw.get('window_minutes')} min wide")
    check("Times are shown in IST, not UTC",
          bool(tw.get("start_ist")) and bool(tw.get("end_ist")),
          f"{tw.get('start_ist')} - {tw.get('end_ist')} IST")
    check("Lead time is positive (there is time to intercept)",
          tw.get("minutes_from_now", -1) >= 0,
          f"{tw.get('minutes_from_now')} min of lead time")

    # ── 7. Accuracy is self-reported from the training run ────────────────
    section("7. MODEL SCORECARD CARRIED IN THE PAYLOAD")
    sc = alert.get("model_scorecard", {})
    check("Payload carries measured held-out accuracy",
          bool(sc.get("top5_hit_rate")),
          f"Top-1 {sc.get('top1_hit_rate')} | Top-5 {sc.get('top5_hit_rate')} "
          f"| NDCG@5 {sc.get('ndcg_at_5')} | n={sc.get('evaluated_on_queries')}")

    # ── The actual alert, as the officer sees it ──────────────────────────
    section("WHAT THE OFFICER SEES")
    print(f"  Case          : {alert.get('case_id')}")
    print(f"  Mule account  : {alert.get('mule_account_id')}")
    print(f"  Amount        : Rs.{alert.get('compromised_amount', 0):,.0f}")
    print(f"  Intercept from: {tw.get('start_ist')} to {tw.get('end_ist')} IST")
    print(f"  Lead time     : {tw.get('minutes_from_now')} min")
    print(f"  Searched      : {alert.get('total_candidates_evaluated')} cash points\n")
    for a in atms:
        print(f"   #{a['rank']} [{a.get('risk_tier','?'):8}] {a.get('probability_pct',0):5.1f}%  "
              f"{a.get('bank_name')} — ETA {a.get('patrol_eta_mins')} min")
        print(f"        {a.get('explanation')}")

    summarize()


def summarize():
    section("VERIFICATION SUMMARY")
    passed = sum(1 for _, ok in _results if ok)
    total = len(_results)
    failed = [n for n, ok in _results if not ok]
    print(f"  {passed}/{total} checks passed")
    if failed:
        print("\n  FAILED CHECKS — fix before presenting:")
        for n in failed:
            print(f"    - {n}")
        sys.exit(1)
    print("\n  ALL CHECKS PASSED. The full chain works end to end:")
    print("  bank feed -> backend -> ML engine -> WebSocket -> dashboard.")


if __name__ == "__main__":
    main()
