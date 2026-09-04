"""
Project Drishti — ML Engine
File: ml_engine/pipelines/explainability.py
Role: Role 2 — ML/AI Engineer

Turns model output into a dispatch justification an officer can act on and a
supervisor can audit. Nothing in this system is allowed to say "the model said
so" — a patrol deployment based on an unexplained score is not defensible.

Phase 1: Template explanations (works with zero dependencies).
Phase 2: SHAP TreeExplainer attributions when LambdaMART is live.

TWO BUGS THIS MODULE USED TO HAVE, BOTH WORTH UNDERSTANDING
-----------------------------------------------------------
1. It read feature values with `candidate.get("mule_network_affinity")`. Those
   features live in the FEATURE VECTOR, not on the candidate dict, so the lookup
   always returned the 0 default and printed "used by 0 linked mule accounts" as
   a reason to send a patrol. Values are now read positionally from the same
   feature matrix SHAP was computed on, so the text cannot drift from the model.

2. It phrased any positive SHAP attribution as supporting evidence, even when
   the underlying feature value was 0. "0 prior frauds" is not a reason to go
   somewhere. Count-like features are now suppressed unless their value is
   actually non-zero — an explanation that cites non-evidence is worse than no
   explanation, because it manufactures false confidence.
"""

from typing import Any, Dict, List, Optional

# TreeExplainer construction walks the whole booster, which is pure overhead to
# repeat per alert when the model never changes between requests. Cached by model
# identity so a retrain-and-reload still builds a fresh explainer.
_explainer_cache: Dict[int, Any] = {}


def _get_explainer(model):
    key = id(model)
    if key not in _explainer_cache:
        import shap
        _explainer_cache[key] = shap.TreeExplainer(model)
        print("[Explainability] SHAP TreeExplainer built and cached.")
    return _explainer_cache[key]


# Count-like features that are only meaningful when non-zero. A positive SHAP
# attribution on one of these with value 0 is an artefact of the tree structure,
# not evidence, and must never be shown to an officer.
_REQUIRES_NONZERO = {
    "historical_fraud_count",
    "mule_atm_affinity",
    "mule_network_affinity",
    "h3_fraud_density",
    "is_weekend",
    "is_night",
}


def _fraud_label(count: float) -> str:
    c = int(count)
    if c == 0:
        return "no recorded fraud history"
    if c <= 2:
        return f"{c} prior fraud incident(s) recorded here"
    if c <= 5:
        return f"{c} confirmed fraud incidents (high-risk cash point)"
    return f"{c} confirmed fraud incidents (VERY HIGH risk cash point)"


def _travel_label(mins: float) -> str:
    if mins <= 5:
        return f"immediately reachable (~{mins:.0f} min drive)"
    if mins <= 15:
        return f"close proximity (~{mins:.0f} min drive)"
    if mins <= 30:
        return f"moderate distance (~{mins:.0f} min drive)"
    return f"distant (~{mins:.0f} min drive)"


def _positive_phrase(fname: str, val: float) -> Optional[str]:
    """Officer-facing phrasing for a feature that PUSHED the ranking UP."""
    if fname == "travel_time_mins":
        return _travel_label(val)
    if fname == "distance_km":
        return f"{val:.1f} km by road"
    if fname == "historical_fraud_count":
        return _fraud_label(val)
    if fname == "mule_atm_affinity":
        return f"THIS mule has cashed out here before ({int(val)}x)"
    if fname == "mule_network_affinity":
        return f"{int(val)} prior cash-outs by linked mules operating in this syndicate zone"
    if fname == "h3_fraud_density":
        return f"dense fraud cluster in the surrounding ~5 km ({int(val)} incidents)"
    if fname == "is_night":
        return "night-time window (elevated mule activity)"
    if fname == "is_weekend":
        return "weekend timing pattern"
    if fname == "atm_type_encoded":
        return "cash-point type favoured by runners (Banking Correspondent)"
    if fname == "hour_of_day":
        return f"time-of-day pattern ({int(val):02d}:00 IST)"
    return None


def _negative_phrase(fname: str, val: float) -> Optional[str]:
    """Phrasing for a feature that PUSHED the ranking DOWN — shown as a caveat."""
    if fname == "travel_time_mins":
        return f"but {val:.0f} min away, so a runner may reach a closer point first"
    if fname == "distance_km":
        return f"but {val:.1f} km out"
    if fname == "historical_fraud_count":
        return "but no significant fraud history here"
    if fname == "mule_atm_affinity":
        return "but this mule has no prior use of this point"
    if fname == "mule_network_affinity":
        return "but no known syndicate activity here"
    if fname == "h3_fraud_density":
        return "but a low-crime neighbourhood"
    return None


def generate_template_explanation(candidate: Dict[str, Any], rank: int) -> str:
    """
    Model-free explanation from the candidate's own fields. Used whenever the
    heuristic fallback is serving, so the UI never shows a blank reason.
    """
    travel = float(candidate.get("travel_time_mins", 0) or 0)
    fraud = float(candidate.get("historical_fraud_count", 0) or 0)
    reasons = [_travel_label(travel), _fraud_label(fraud)]
    return f"Rank #{rank}: {' + '.join(reasons)}."


def generate_shap_explanations(
    model,
    feature_matrix,
    candidate_atms: List[Dict],
    feature_names: List[str],
) -> List[str]:
    """
    SHAP TreeExplainer attributions translated into dispatch language.

    Feature values are read from `feature_matrix` (the exact rows the model
    scored), never from the candidate dict — so the explanation is guaranteed to
    describe what the model actually saw.
    """
    try:
        import numpy as np
        import shap
    except ImportError:
        print("[Explainability] SHAP unavailable - using template explanations.")
        return [generate_template_explanation(c, i + 1) for i, c in enumerate(candidate_atms)]

    try:
        explainer = _get_explainer(model)
        shap_values = np.asarray(explainer.shap_values(feature_matrix))
    except Exception as e:
        print(f"[Explainability] SHAP failed ({e}) - using template explanations.")
        return [generate_template_explanation(c, i + 1) for i, c in enumerate(candidate_atms)]

    idx = {n: i for i, n in enumerate(feature_names)}
    explanations: List[str] = []

    for i, (atm, shap_row) in enumerate(zip(candidate_atms, shap_values)):
        row_vals = feature_matrix[i]

        def value_of(fname: str) -> float:
            j = idx.get(fname)
            return float(row_vals[j]) if j is not None and j < len(row_vals) else 0.0

        scored = []
        for sv, fname in zip(shap_row, feature_names):
            val = value_of(fname)
            # Drop attributions that cite non-evidence (a zero count).
            if fname in _REQUIRES_NONZERO and val == 0:
                continue
            scored.append((float(sv), fname, val))

        drivers = sorted([s for s in scored if s[0] > 0], key=lambda t: -t[0])
        suppressors = sorted([s for s in scored if s[0] < 0], key=lambda t: t[0])

        parts: List[str] = []
        seen = set()
        for sv, fname, val in drivers:
            phrase = _positive_phrase(fname, val)
            # distance_km and travel_time_mins say the same thing to a human —
            # citing both wastes the officer's attention.
            key = "proximity" if fname in ("travel_time_mins", "distance_km") else fname
            if phrase and key not in seen:
                parts.append(phrase)
                seen.add(key)
            if len(parts) == 2:
                break

        # Fall back to the plain facts rather than emitting a bare score.
        if not parts:
            parts.append(_travel_label(value_of("travel_time_mins")))
            fc = value_of("historical_fraud_count")
            if fc > 0:
                parts.append(_fraud_label(fc))

        caveat = ""
        for sv, fname, val in suppressors[:1]:
            # Only surface a caveat with real weight relative to this row.
            if abs(sv) > 0.05 * (abs(shap_row).max() or 1.0):
                phrase = _negative_phrase(fname, val)
                key = "proximity" if fname in ("travel_time_mins", "distance_km") else fname
                if phrase and key not in seen:
                    caveat = f" — {phrase}"

        explanations.append(f"Rank #{i + 1}: {' + '.join(parts)}{caveat}.")

    return explanations


def generate_explanations(
    top_candidates: List[Dict[str, Any]],
    model=None,
    feature_matrix=None,
    feature_names: Optional[List[str]] = None,
    model_used: str = "FallbackHeuristic",
) -> List[str]:
    """Routes to SHAP when a real model is serving, templates otherwise."""
    if model_used == "LambdaMART" and model is not None and feature_matrix is not None:
        print("[Explainability] Using SHAP attributions (LambdaMART).")
        return generate_shap_explanations(model, feature_matrix, top_candidates,
                                          feature_names or [])
    print("[Explainability] Using template explanations (heuristic mode).")
    return [generate_template_explanation(c, i + 1) for i, c in enumerate(top_candidates)]


# ─── Self-test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cands = [
        {"bank_name": "HDFC", "travel_time_mins": 7,  "historical_fraud_count": 8},
        {"bank_name": "SBI",  "travel_time_mins": 2,  "historical_fraud_count": 6},
        {"bank_name": "UBI",  "travel_time_mins": 40, "historical_fraud_count": 7},
        {"bank_name": "PNB",  "travel_time_mins": 21, "historical_fraud_count": 0},
    ]
    print("\n[TEST] Template mode (no model):\n")
    for e in generate_explanations(cands, model_used="FallbackHeuristic"):
        print(f"  {e}")
