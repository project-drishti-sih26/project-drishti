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

  // Resolve risk score (0.0 to 1.0 or 0 to 100)
  let rawScore = rawLoc.riskScore ?? rawLoc.risk_score ?? rawLoc.score ?? rawLoc.probability ?? 0.75;
  let riskScore = Number(rawScore);
  if (isNaN(riskScore)) riskScore = 0.75;
  if (riskScore > 1.0) riskScore = riskScore / 100.0; // convert 0-100 scale to 0.0-1.0
  riskScore = Math.min(Math.max(riskScore, 0), 1.0);

  // Resolve target type (ATM, Bank Branch, BC Point)
  let type = String(rawLoc.type ?? rawLoc.target_type ?? rawLoc.category ?? 'ATM').trim();
  const lowerType = type.toLowerCase();
  if (lowerType.includes('branch') || lowerType.includes('bank') && !lowerType.includes('atm')) {
    type = 'Bank Branch';
  } else if (lowerType.includes('bc') || lowerType.includes('csp') || lowerType.includes('point') || lowerType.includes('correspondent')) {
    type = 'BC Point';
  } else {
    type = 'ATM';
  }

  // Risk Tier calculation
  let riskTier = rawLoc.riskTier || rawLoc.risk_tier;
  if (!riskTier) {
    if (riskScore >= 0.90) riskTier = 'CRITICAL';
    else if (riskScore >= 0.75) riskTier = 'HIGH';
    else if (riskScore >= 0.60) riskTier = 'MEDIUM';
    else riskTier = 'LOW';
  }

  const rank = Number(rawLoc.rank ?? fallbackRank);

  return {
    id: String(rawLoc.id ?? rawLoc.target_id ?? rawLoc.code ?? `target-${rank}`),
    name: String(rawLoc.name ?? rawLoc.target_name ?? `${type} Target #${rank}`),
    type: type,
    latitude: hasValidCoords ? latitude : null,
    longitude: hasValidCoords ? longitude : null,
    hasValidCoords: hasValidCoords,
    h3Index: rawLoc.h3Index ?? rawLoc.h3_index ?? null,
    riskScore: riskScore,
    scorePercent: Math.round(riskScore * 100),
    rank: isNaN(rank) ? fallbackRank : rank,
    address: rawLoc.address ?? rawLoc.location_address ?? 'Location address unavailable',
    travelTime: rawLoc.travelTime ?? rawLoc.travel_time ?? (rawLoc.eta_minutes ? `${rawLoc.eta_minutes} mins` : null),
    expectedWindow: (typeof rawLoc.expectedWindow === 'object' && rawLoc.expectedWindow !== null)
      ? `${rawLoc.expectedWindow.min ?? 10}–${rawLoc.expectedWindow.max ?? 25} mins`
      : (typeof rawLoc.withdrawal_window === 'object' && rawLoc.withdrawal_window !== null)
      ? `${rawLoc.withdrawal_window.min ?? 10}–${rawLoc.withdrawal_window.max ?? 25} mins`
      : (typeof rawLoc.expectedWindow === 'string' ? rawLoc.expectedWindow : (typeof rawLoc.withdrawal_window === 'string' ? rawLoc.withdrawal_window : (rawLoc.window_min && rawLoc.window_max ? `${rawLoc.window_min}–${rawLoc.window_max} mins` : '15–30 mins'))),
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
  
  // Normalize targets array
  const rawTargets = Array.isArray(rawAlert.targets) ? rawAlert.targets : 
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
  let withdrawalWindow = '20–45 mins';
  if (typeof rawAlert.withdrawal_window === 'object' && rawAlert.withdrawal_window !== null) {
    const min = rawAlert.withdrawal_window.min ?? rawAlert.withdrawal_window.minimum ?? 15;
    const max = rawAlert.withdrawal_window.max ?? rawAlert.withdrawal_window.maximum ?? 45;
    withdrawalWindow = `${min}–${max} mins`;
  } else if (typeof rawAlert.withdrawal_window === 'string') {
    withdrawalWindow = rawAlert.withdrawal_window;
  }

  // Explanations / SHAP reasons
  let explanation = [];
  if (Array.isArray(rawAlert.explanation)) {
    explanation = rawAlert.explanation.map(String);
  } else if (Array.isArray(rawAlert.reasons)) {
    explanation = rawAlert.reasons.map(String);
  } else if (typeof rawAlert.explanation === 'string') {
    explanation = [rawAlert.explanation];
  } else {
    explanation = [
      'High proximity to recent mule account activity',
      'Historical cash withdrawal velocity anomaly',
      'Optimal road-network travel corridor match'
    ];
  }

  return {
    alertId,
    caseId: rawAlert.case_id || rawAlert.caseId || 'CASE-ACTIVE',
    muleAccount: rawAlert.mule_account || rawAlert.muleAccount || 'XXXX-XXXX-8821',
    defraudedAmount: rawAlert.defrauded_amount || rawAlert.amount || '₹ 1,50,000',
    incidentTimestamp: rawAlert.incident_timestamp || rawAlert.timestamp || new Date().toISOString(),
    riskScore: Number(rawAlert.risk_score ?? rawAlert.riskScore ?? 0.92),
    withdrawalWindow,
    targets,
    riskCells,
    explanation,
    originLat: Number(rawAlert.origin_lat ?? rawAlert.originLatitude ?? 28.6289),
    originLng: Number(rawAlert.origin_lng ?? rawAlert.originLongitude ?? 77.2065),
    raw: rawAlert
  };
};

export default {
  normalizeTargetLocation,
  normalizeAlertData
};
