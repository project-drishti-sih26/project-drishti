/**
 * Data Normalization Utility (Role 3 - GIS Radar)
 * Project Drishti - Tactical Predictive Analytics System for Cybercrime Complaints
 * 
 * Decouples the GIS map visualization layer from raw backend REST API / WebSocket payloads.
 * Normalizes varying backend response schemas into consistent GIS entities.
 */

/**
 * Normalizes a raw location / target record into standard GIS target format.
 * 
 * @param {Object} rawLoc - Raw target record from ML engine or database
 * @param {number} [fallbackRank=1] - Fallback rank index if missing
 * @returns {Object} Normalized target location object
 */
export const normalizeTargetLocation = (rawLoc = {}, fallbackRank = 1) => {
  if (!rawLoc || typeof rawLoc !== 'object') {
    return null;
  }

  // Handle various coordinate naming conventions (latitude/lat, longitude/lng/lon)
  const latitude = Number(rawLoc.latitude ?? rawLoc.lat ?? rawLoc.y ?? NaN);
  const longitude = Number(rawLoc.longitude ?? rawLoc.lng ?? rawLoc.lon ?? rawLoc.x ?? NaN);

  // Validate coordinates
  const hasValidCoords = !isNaN(latitude) && !isNaN(longitude) &&
    latitude >= -90 && latitude <= 90 &&
    longitude >= -180 && longitude <= 180;

  // Resolve risk score (0.0 to 1.0 or 0 to 100).
  //
  // `confidence_score` / `probability_pct` are what the ML engine actually
  // emits per ATM. Neither was in this list, so EVERY live target fell through
  // to the 0.75 default: the map painted all five hexagons the same amber and
  // the details panel read "75%" for a target the model had scored at 4%.
  // Worse, `risk_tier` below WAS read correctly, so a target could render as
  // CRITICAL and 75% simultaneously.
  let rawScore = rawLoc.confidence_score ?? rawLoc.riskScore ?? rawLoc.risk_score ??
    rawLoc.probability_pct ?? rawLoc.score ?? rawLoc.probability ?? null;
  const hasRealScore = rawScore !== null && rawScore !== undefined && !isNaN(Number(rawScore));
  let riskScore = hasRealScore ? Number(rawScore) : 0;
  if (riskScore > 1.0) riskScore = riskScore / 100.0; // convert 0-100 scale to 0.0-1.0
  riskScore = Math.min(Math.max(riskScore, 0), 1.0);

  // Resolve target type (ATM, Bank Branch, BC Point).
  // `location_type` is the field the ML engine emits; without it every live
  // target, including bank branches and BC points, was labelled "ATM".
  let type = String(rawLoc.location_type ?? rawLoc.type ?? rawLoc.target_type ?? rawLoc.category ?? 'ATM').trim();
  const lowerType = type.toLowerCase();
  if (lowerType.includes('branch') || lowerType.includes('bank') && !lowerType.includes('atm')) {
    type = 'Bank Branch';
  } else if (lowerType.includes('bc') || lowerType.includes('csp') || lowerType.includes('point') || lowerType.includes('correspondent')) {
    type = 'BC Point';
  } else {
    type = 'ATM';
  }

  // Risk Tier. Prefer the backend's own tier — it is cut on the calibrated
  // probability scale, where the top pick of ~170 candidates is CRITICAL at
  // ~44%, not at 90%. The local thresholds below mirror the engine's
  // `_risk_tier` so a fallback classification agrees with a served one.
  let riskTier = rawLoc.riskTier || rawLoc.risk_tier;
  if (!riskTier) {
    if (riskScore >= 0.30) riskTier = 'CRITICAL';
    else if (riskScore >= 0.15) riskTier = 'HIGH';
    else if (riskScore >= 0.06) riskTier = 'MEDIUM';
    else riskTier = 'LOW';
  }

  const rank = Number(rawLoc.rank ?? fallbackRank);

  // Travel time. `travel_time_mins` / `patrol_eta_mins` are the engine's real
  // fields — absent from the old list, so the tactical panel showed no ETA at
  // all on live alerts, which is the one number a dispatcher needs most.
  const etaMins = rawLoc.travel_time_mins ?? rawLoc.patrol_eta_mins ?? rawLoc.eta_minutes ?? null;

  return {
    id: String(rawLoc.location_id ?? rawLoc.id ?? rawLoc.target_id ?? rawLoc.code ?? `target-${rank}`),
    name: String(rawLoc.bank_name ? `${rawLoc.bank_name} ATM` : (rawLoc.name ?? rawLoc.target_name ?? `${type} Target #${rank}`)),
    type: type,
    latitude: hasValidCoords ? latitude : null,
    longitude: hasValidCoords ? longitude : null,
    hasValidCoords: hasValidCoords,
    h3Index: rawLoc.h3Index ?? rawLoc.h3_index ?? null,
    riskScore: riskScore,
    hasRealScore: hasRealScore,
    scorePercent: hasRealScore ? Math.round(riskScore * 100) : null,
    rank: isNaN(rank) ? fallbackRank : rank,
    address: rawLoc.address ?? rawLoc.location_address ?? 'Location address unavailable',
    distanceKm: rawLoc.distance_km ?? rawLoc.distanceKm ?? null,
    historicalFraudCount: rawLoc.historical_fraud_count ?? null,
    explanation: rawLoc.explanation ?? null,
    travelTime: rawLoc.travelTime ?? rawLoc.travel_time
      ?? (etaMins !== null && !isNaN(Number(etaMins)) ? `${Math.round(Number(etaMins))} mins` : null),
    // The interception window is a property of the CASE (one survival-model
    // prediction), not of an individual ATM. Inventing a per-target
    // "15-30 mins" implied five separate predictions that were never made.
    expectedWindow: (typeof rawLoc.expectedWindow === 'object' && rawLoc.expectedWindow !== null)
      ? `${rawLoc.expectedWindow.min ?? 10}–${rawLoc.expectedWindow.max ?? 25} mins`
      : (typeof rawLoc.withdrawal_window === 'object' && rawLoc.withdrawal_window !== null)
      ? `${rawLoc.withdrawal_window.min ?? 10}–${rawLoc.withdrawal_window.max ?? 25} mins`
      : (typeof rawLoc.expectedWindow === 'string' ? rawLoc.expectedWindow
        : (typeof rawLoc.withdrawal_window === 'string' ? rawLoc.withdrawal_window
          : (rawLoc.window_min && rawLoc.window_max ? `${rawLoc.window_min}–${rawLoc.window_max} mins` : null))),
    riskTier: riskTier.toUpperCase(),
    raw: rawLoc
  };
};

/**
 * Normalizes an incoming prediction alert (e.g. from REST API or WebSocket)
 * into a standardized GIS alert payload.
 * 
 * @param {Object} rawAlert - Raw alert payload
 * @returns {Object} Standardized GIS alert object
 */
export const normalizeAlertData = (rawAlert = {}) => {
  if (!rawAlert || typeof rawAlert !== 'object') {
    return null;
  }

  const alertId = String(rawAlert.alert_id ?? rawAlert.id ?? rawAlert.case_id ?? `ALT-${Date.now().toString().slice(-4)}`);
  
  // Normalize targets array (supports backend `top_5_atms` as well as mock `targets`)
  const rawTargets = Array.isArray(rawAlert.top_5_atms) ? rawAlert.top_5_atms :
                     Array.isArray(rawAlert.targets) ? rawAlert.targets : 
                     Array.isArray(rawAlert.predicted_locations) ? rawAlert.predicted_locations : 
                     Array.isArray(rawAlert.locations) ? rawAlert.locations : [];

  const targets = rawTargets
    .map((loc, idx) => normalizeTargetLocation(loc, idx + 1))
    .filter(Boolean);

  // Normalize risk cells (Uber H3 hex indexes)
  const rawCells = Array.isArray(rawAlert.risk_cells) ? rawAlert.risk_cells :
                   Array.isArray(rawAlert.h3_cells) ? rawAlert.h3_cells :
                   Array.isArray(rawAlert.danger_zones) ? rawAlert.danger_zones : [];

  const riskCells = rawCells.map((cell, idx) => {
    if (typeof cell === 'string') {
      return {
        id: `cell-${idx}`,
        h3Index: cell,
        riskTier: 'HIGH',
        score: 0.85
      };
    }
    const score = Number(cell.score ?? cell.risk_score ?? cell.riskScore ?? 0.8);
    const riskTier = String(cell.riskTier ?? cell.risk_tier ?? (score >= 0.9 ? 'CRITICAL' : score >= 0.75 ? 'HIGH' : score >= 0.6 ? 'MEDIUM' : 'LOW')).toUpperCase();
    return {
      id: cell.id || `cell-${idx}`,
      h3Index: cell.h3Index || cell.h3_index || cell.index || null,
      riskTier: riskTier,
      score: score,
      description: cell.description || cell.name || `H3 Zone #${idx + 1}`
    };
  }).filter((c) => c.h3Index);

  // Withdrawal time window formatting
  let withdrawalWindow = null;
  if (typeof rawAlert.time_window === 'object' && rawAlert.time_window !== null) {
    const tw = rawAlert.time_window;
    const mins = tw.minutes_from_now;
    // start_ist / end_ist are pre-formatted IST by the engine. Parsing `.end`
    // and slicing the ISO string yields UTC, which is an hour-and-a-half wrong
    // on an officer's screen.
    if (tw.start_ist && tw.end_ist) {
      withdrawalWindow = typeof mins === 'number'
        ? `${tw.start_ist}–${tw.end_ist} IST (in ${mins} min)`
        : `${tw.start_ist}–${tw.end_ist} IST`;
    } else if (typeof mins === 'number') {
      withdrawalWindow = `${mins} mins`;
    }
  } else if (typeof rawAlert.withdrawal_window === 'object' && rawAlert.withdrawal_window !== null) {
    const min = rawAlert.withdrawal_window.min ?? rawAlert.withdrawal_window.minimum ?? 15;
    const max = rawAlert.withdrawal_window.max ?? rawAlert.withdrawal_window.maximum ?? 45;
    withdrawalWindow = `${min}–${max} mins`;
  } else if (typeof rawAlert.withdrawal_window === 'string') {
    withdrawalWindow = rawAlert.withdrawal_window;
  }

  // Explanations / SHAP reasons.
  //
  // The engine attaches a SHAP-derived explanation to EACH ranked target; there
  // is no alert-level explanation field. This block used to fall through to
  // three hardcoded strings ("High proximity to recent mule account
  // activity", ...) — generic text that looks exactly like model output and
  // appears on every live alert regardless of what the model actually found.
  // Fabricated reasoning on a dispatch screen is the worst failure this UI can
  // have, so the real per-target attributions are lifted instead.
  let explanation = [];
  if (Array.isArray(rawAlert.explanation)) {
    explanation = rawAlert.explanation.map(String);
  } else if (Array.isArray(rawAlert.reasons)) {
    explanation = rawAlert.reasons.map(String);
  } else if (typeof rawAlert.explanation === 'string') {
    explanation = [rawAlert.explanation];
  } else {
    explanation = targets
      .map((t) => t.explanation)
      .filter((e) => typeof e === 'string' && e.length > 0);
  }

  // Origin = the mule's last known location, as sent by the engine. Defaulting
  // to fixed coordinates put the origin marker and every distance ring drawn
  // from it in the wrong place whenever the field name did not match.
  const originLat = Number(rawAlert.mule_last_latitude ?? rawAlert.origin_lat ?? rawAlert.originLatitude ?? NaN);
  const originLng = Number(rawAlert.mule_last_longitude ?? rawAlert.origin_lng ?? rawAlert.originLongitude ?? NaN);
  const originKnown = !isNaN(originLat) && !isNaN(originLng) &&
    (rawAlert.mule_location_known !== false);

  return {
    alertId,
    caseId: rawAlert.case_id || rawAlert.caseId || 'CASE-ACTIVE',
    muleAccount: rawAlert.mule_account_id || rawAlert.mule_account || rawAlert.muleAccount || 'XXXX-XXXX-8821',
    defraudedAmount: rawAlert.compromised_amount ? `₹ ${Number(rawAlert.compromised_amount).toLocaleString('en-IN')}` : (rawAlert.defrauded_amount || rawAlert.amount || '₹ 1,50,000'),
    incidentTimestamp: rawAlert.detected_at || rawAlert.incident_timestamp || rawAlert.timestamp || new Date().toISOString(),
    detectedAtIst: rawAlert.detected_at_ist || null,
    // Alert-level confidence = the calibrated probability of the top-ranked
    // target. The old 0.92 default was a number no model ever produced.
    riskScore: Number(
      rawAlert.risk_score ?? rawAlert.riskScore ?? (targets[0] ? targets[0].riskScore : 0)
    ),
    withdrawalWindow,
    windowSource: (typeof rawAlert.time_window === 'object' && rawAlert.time_window)
      ? rawAlert.time_window.model_source || null : null,
    modelUsed: rawAlert.model_used || null,
    // Surfaced so the GIS view can refuse to present a heuristic as a prediction.
    degraded: rawAlert.degraded === true,
    degradedReason: rawAlert.degraded_reason || null,
    totalCandidatesEvaluated: rawAlert.total_candidates_evaluated ?? null,
    top5ProbabilityMass: rawAlert.top5_probability_mass ?? null,
    modelScorecard: rawAlert.model_scorecard || null,
    targets,
    riskCells,
    explanation,
    originKnown,
    originLat: originKnown ? originLat : 28.6289,
    originLng: originKnown ? originLng : 77.2065,
    raw: rawAlert
  };
};

export default {
  normalizeTargetLocation,
  normalizeAlertData
};
