# Project Drishti — Verified Pitch Sheet

**PS ID SIH26184 · I4C / Ministry of Home Affairs**

Every number in this file was measured on this machine on **4 Sep 2026** by
`verify_e2e.py` (26/26 pass), `frontend/verify_gis_normalizer.mjs` (18/18 pass),
and the model scorecard embedded in each live alert payload. Anything I could
**not** verify is in the "Say this carefully" section at the end — read that
before you go on stage.

---

## 1. The problem, in one breath

A citizen is defrauded. Money lands in a mule account. Within roughly 20–40
minutes it leaves the banking system as **physical cash at an ATM** — and at
that moment it becomes unrecoverable and untraceable.

Everything Indian cyber-policing currently does is *after* that moment: NCRP
complaint, freeze request, chargeback attempt. All of it races money that has
already left.

**Drishti attacks the only window that still exists: the gap between the debit
and the withdrawal.** It does not try to recover money. It tries to put a patrol
at the right cash machine before the runner arrives.

## 2. What the system actually does

The instant a flagged mule account is credited, Drishti answers three questions
and pushes the answer to a dashboard in **under 100 ms**:

| Question | Model | Output |
|---|---|---|
| **WHERE** will the cash come out? | LambdaMART learning-to-rank over every reachable cash point | Ranked top-5 with calibrated probabilities |
| **WHEN** will it come out? | Cox proportional-hazards survival model | A case-specific IST interception window |
| **WHY** this location? | SHAP attributions on the ranker | One plain-language sentence per target |

Measured on the last E2E run:

```
Case          : CYB-E2E-1788503691
Amount        : Rs.125,000
Intercept from: 12:18 to 12:31 IST      (14 min of lead time)
Searched      : 168 reachable cash points

 #1 [CRITICAL]  42.9%  ICICI Bank — ETA 4.5 min
      2.1 km by road + 92 prior cash-outs by linked mules in this syndicate zone
 #2 [HIGH    ]  22.5%  HDFC Bank — ETA 7.9 min
 #3 [MEDIUM  ]  12.2%  HDFC Bank — ETA 5.2 min
 #4 [MEDIUM  ]   6.9%  Union Bank — ETA 11.6 min
 #5 [MEDIUM  ]   6.7%  HDFC Bank — ETA 2.8 min
```

Note rank #5: **2.8 min away, and the model still ranks it fifth.** That is the
whole thesis in one line — proximity is a feature, not the answer.

## 3. Numbers you can defend

### Ranking accuracy — 577 held-out queries the model never saw

| Metric | Drishti (LambdaMART) |
|---|---|
| Top-1 hit rate | **55.1%** |
| Top-3 | **81.6%** |
| Top-5 | **89.4%** |
| Top-10 | **95.8%** |
| NDCG@5 | **0.741** |
| MRR | **0.701** |

### Versus the baselines a skeptical judge will propose

| Approach | Top-1 | Top-5 |
|---|---|---|
| Random guess | 0.9% | 6.1% |
| **"Just send them to the nearest ATM"** | 14.0% | 66.4% |
| "Just watch the worst hotspot" | 5.4% | 28.1% |
| Hand-tuned heuristic (distance + crime + history) | 27.4% | 45.9% |
| **Drishti** | **55.1%** | **89.4%** |

The nearest-ATM baseline is the one that matters, because it is what a station
would do without us. Drishti is **~4× better at rank 1** than sending the patrol
to the closest machine.

### Timing model

- Cox **C-index 0.6127** (case-specific ordering of withdrawal delays)
- Kaplan-Meier population median **19.7 min**, IQR **14–30 min**
- Fitted on **3,559** debit→withdrawal episodes (2,889 observed, **670
  right-censored** — 18.8%)
- Hazard ratios: `mule_tier` **1.175** (higher-tier mules cash out faster),
  `travel_mins` **0.951** (farther targets take longer). Both signs are
  physically correct — this is the sanity check that proves the model learned
  mechanics, not noise.

### Calibration honesty

Temperature scaling (T = 0.18) fitted on held-out validation. On the test set
the model **claims 50.1% confidence and is actually right 55.3% of the time** —
a 5.2-point gap in the *cautious* direction. It under-promises. For a dispatch
tool that is the correct direction to be wrong in.

### Scale and latency

- **325,580** training rows across **3,559** cases
- **168** cash points indexed and re-scored per alert
- Alert generated in **50–58 ms** end to end (bank feed → backend → ML → WebSocket → browser), against a 5-second budget
- Two-stage spatial retrieval: Uber **H3** `grid_disk` coarse filter, then exact
  Haversine + road-network factor

---

## 4. Why these model choices (the questions judges actually ask)

**"Why learning-to-rank and not a classifier?"**
Roughly 99.4% of candidates are negatives. A classifier optimises average
correctness and learns to say "no" to everything. A patrol does not need a
probability per ATM — it needs a *correctly ordered shortlist*. LambdaMART
optimises the ordering directly, which is the actual operational object.

**"Why survival analysis and not a regression on minutes?"**
18.8% of our withdrawal episodes are **right-censored** — we know the cash had
not come out yet when observation ended, but not when it eventually did.
Regression must either delete that data (biasing toward fast withdrawals) or
treat the censoring time as the truth (which is simply false). Cox handles
censoring natively. This is the single most defensible modelling decision in
the project.

**"What happens when the model can't run?"**
There is an explicit three-tier degradation ladder: **Cox** (case-specific) →
**Kaplan-Meier** (population curve) → **statistical prior**. Whichever tier
served the answer is stamped into the payload as `window_source` and shown on
the dashboard. If the system falls back to a heuristic, the banner turns dark
red and reads *"DEGRADED — HEURISTIC, NOT A PREDICTION. Do not dispatch on these
rankings."*

**"How do I know the dashboard is showing me the model and not a mock-up?"**
That is the provenance strip across the top of every screen. It reads:

```
● LIVE PREDICTION | Ranker: LambdaMART | Window: CoxProportionalHazards
| Intercept 12:18–12:31 IST | 168 cash points searched
| Top-5 holds 88% of probability
| Held-out accuracy: Top-1 55.1%, Top-5 89.4% (n=577 unseen cases) | WS connected
```

When no live alert has arrived it turns amber and says **"○ Sample case
(awaiting live alert)"**. The dashboard cannot lie about whether it is live —
and the four illustrative tiles are labelled *"Illustrative — not model output"*
in the UI itself.

---

## 5. Demo script (3 minutes)

1. **Dashboard, before anything fires.** Point at the amber strip: *"this says
   Sample case — nothing here is a prediction yet. Watch the strip."*
2. **Fire the transaction** in a terminal:
   ```bash
   python simulation/run_live_demo.py
   ```
3. **Do not refresh.** The WebSocket pushes; the strip goes emerald and names
   both models; the countdown starts; the map flies to rank #1 and draws the H3
   risk hexagons.
4. **Click rank #1.** Read the SHAP sentence aloud: *"2.1 km by road plus 92
   prior cash-outs by linked mules in this syndicate zone."* Then say: *"the
   model can always tell an officer why. This is not a black box telling a
   constable where to drive."*
5. **Click rank #5** — 2.8 minutes away, ranked fifth. *"The nearest machine is
   not the answer. That is what we add over a distance sort, and it is worth
   55% versus 14% at rank one."*
6. **The kill shot, if you have a minute left:** fire a second transaction from
   a different origin. The top-1 confidence drops from ~43% to ~17%, because
   South Delhi has a denser, more ambiguous ATM field. *"It is less confident
   when it should be less confident."*

## 6. Say this carefully — unverified or limited

Be the person who volunteers these. It is worth more than the metrics.

1. **All figures above are on synthetic data.** The generator models spatial
   structure, mule tiers, road-travel times, and withdrawal delays. It does not
   have real I4C case data behind it. Say "on our simulation harness" out loud —
   do not let a judge discover it.
2. **`is_night` and `is_weekend` have zero splits in the trained model.** The
   data generator does not encode time-of-day effects, so the model correctly
   ignored those features. On real data they would almost certainly matter. If
   asked what you would do next, this is your best answer.
3. **CCTV, cell-tower, and patrol-dispatch integrations do not exist.** The UI
   now says *"Not integrated"* wherever it used to invent them. Do not claim
   AVL/CAD integration or camera feeds.
4. **Any national fraud-loss statistic in the older slide deck is unverified** —
   I had no web access to confirm it. Either cite an I4C/NCRP figure you have
   personally checked, or drop the number and describe the mechanism instead.
   The mechanism argument is stronger anyway and cannot be fact-checked against
   you.
5. **Cox C-index 0.6127 is modest.** If challenged: it is meaningfully above
   chance on a genuinely noisy human-behaviour target, and the operational
   output is a 12–15 minute window, not a point estimate — the window width is
   what absorbs that uncertainty.

## 7. Health check before you present

```bash
python verify_e2e.py
```

Expect `26/26 checks passed`. Then:

```bash
node frontend/verify_gis_normalizer.mjs
```

Expect `18/18`. If either fails, the failing line names what broke.

---

## 8. Merge state after pulling Role 4's branch (4 Sep 2026)

Verified after the pull — **all nine honesty-pass markers survived** and the
production build is clean at 414 modules (unchanged), so the conflict resolution
kept our frontend on the files that matter:

| File | What is actually on disk now |
|---|---|
| `CommandCenter.jsx` | **Ours** — has `liveMeta`, the provenance strip, the "Illustrative" labels, and the three-view switcher (`overview` / `spatial_radar` / `live_operations`) |
| `MapRadar.jsx` | **Ours** — has the `hexSource` fix, without which live alerts render zero H3 hexagons |
| `SidebarRight.jsx` | **Ours** — `windowIst`, "Ranked by predicted probability" |
| `CenterRadar.jsx` | **Ours** — real `originLat`/`originLon` |
| `Alerts.jsx`, `CaseFlow.jsx`, `SidebarLeft.jsx` | **Ours** |
| `dataNormalizer.js`, `PredictionDetailsPanel`, `TopTargetsPanel`, `ActiveAlertBanner`, `H3HexLayer` | **Ours** — the `hasRealScore` chain |
| `backend/`, `ml_engine/` | **Ours** (stash) — ML schema alignment, temperature calibration, Cox model |

**Three of Role 4's new components are on disk but orphaned** — nothing imports
them:

- `ui_ux/components/NavSidebar.jsx` (179 lines)
- `ui_ux/components/OverviewView.jsx` (288 lines)
- `ui_ux/components/AllCasesView.jsx` (397 lines)

They are good, prop-driven work (`cases = []` supplied by a parent — no
fabricated internals), but the `CommandCenter` refactor that fed them a `cases`
array lost the conflict, so there is no case store to wire them to. Vite does
not bundle unimported modules, so they cost nothing and cannot break the demo.

**Do not wire them in before presenting.** Afterwards, integrating them needs a
`cases` array in `CommandCenter` — and that list would be mock data, so it must
carry the same "Illustrative — not model output" label the metric tiles do, or
it reintroduces exactly the fabrication class we just removed. Tell Role 4 their
components are preserved, not deleted.

