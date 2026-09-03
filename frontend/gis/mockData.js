/**
 * =========================================================================================
 * ⚠️ DEVELOPMENT-ONLY MOCK FIXTURE — NOT THE PROJECT SOURCE OF TRUTH
 * =========================================================================================
 * This file exists ONLY to allow the GIS frontend (Role 3) to run independently during isolated
 * development while the real data pipeline is unavailable.
 * 
 * OWNERSHIP DEMARCATION:
 * - Role 5 (Data Engineer) owns the `simulation/` directory (`atms_master.csv`, distance matrix,
 *   `run_live_demo.py`, and data generation pipelines).
 * - Role 3 (Maps & GIS Radar) does NOT own or maintain the ATM master dataset or simulation logic.
 * - This mock data contains only a tiny, fictional 6-node fixture for UI testing and will be
 *   swapped with normalized payloads from Role 5 / Backend / ML via `dataNormalizer.js`.
 * =========================================================================================
 */

export const mockLocations = [
  {
    id: "atm-001",
    name: "State Bank ATM - Connaught Place",
    type: "ATM",
    latitude: 28.6315,
    longitude: 77.2167,
    h3Index: "8860145b23fffff",
    riskScore: 0.94,
    rank: 1,
    travelTime: "12 mins",
    address: "Inner Circle, Block B, Connaught Place, New Delhi",
    expectedWindow: "10-25 mins",
    withdrawalProbability: "94%",
    riskTier: "CRITICAL"
  },
  {
    id: "atm-002",
    name: "HDFC 24x7 ATM - Karol Bagh",
    type: "ATM",
    latitude: 28.6514,
    longitude: 77.1907,
    h3Index: "8860145b27fffff",
    riskScore: 0.88,
    rank: 2,
    travelTime: "18 mins",
    address: "Arya Samaj Road, Karol Bagh, New Delhi",
    expectedWindow: "15-35 mins",
    withdrawalProbability: "88%",
    riskTier: "HIGH"
  },
  {
    id: "bc-003",
    name: "Airtel Payments BC Point - Paharganj",
    type: "BC Point",
    latitude: 28.6432,
    longitude: 77.2125,
    h3Index: "8860145b21fffff",
    riskScore: 0.82,
    rank: 3,
    travelTime: "22 mins",
    address: "Main Bazaar, Paharganj, New Delhi",
    expectedWindow: "20-40 mins",
    withdrawalProbability: "82%",
    riskTier: "HIGH"
  },
  {
    id: "branch-004",
    name: "Punjab National Bank - Chandni Chowk Branch",
    type: "Bank Branch",
    latitude: 28.6562,
    longitude: 77.2309,
    h3Index: "8860145b25fffff",
    riskScore: 0.76,
    rank: 4,
    travelTime: "29 mins",
    address: "Netaji Subhash Marg, Chandni Chowk, Delhi",
    expectedWindow: "25-50 mins",
    withdrawalProbability: "76%",
    riskTier: "MEDIUM"
  },
  {
    id: "atm-005",
    name: "ICICI Bank ATM - Rajendra Place",
    type: "ATM",
    latitude: 28.6425,
    longitude: 77.1786,
    h3Index: "8860145b29fffff",
    riskScore: 0.69,
    rank: 5,
    travelTime: "34 mins",
    address: "Pusa Road, Rajendra Place, New Delhi",
    expectedWindow: "30-60 mins",
    withdrawalProbability: "69%",
    riskTier: "MEDIUM"
  },
  {
    id: "bc-006",
    name: "Paytm DigiKendra BC Point - Patel Nagar",
    type: "BC Point",
    latitude: 28.6538,
    longitude: 77.1644,
    h3Index: "8860145b2dfffff",
    riskScore: 0.58,
    rank: 6,
    travelTime: "40 mins",
    address: "East Patel Nagar Market, New Delhi",
    expectedWindow: "35-70 mins",
    withdrawalProbability: "58%",
    riskTier: "LOW"
  }
];

/**
 * Future-ready backend alert contract simulation structure.
 * Decoupled so mock data can easily be swapped with REST / WebSocket payloads.
 */
export const mockActiveAlert = {
  alert_id: "ALT-CYBER-2026-089",
  case_id: "CASE-9921-ND",
  mule_account: "XXXX-XXXX-8821 (SBI)",
  defrauded_amount: "₹ 1,85,000",
  incident_timestamp: new Date().toISOString(),
  origin_lat: 28.6289,
  origin_lng: 77.2065,
  risk_score: 0.94,
  withdrawal_window: {
    min: 15,
    max: 45
  },
  targets: mockLocations,
  risk_cells: [
    { h3Index: "8860145b23fffff", riskTier: "CRITICAL", score: 0.94 },
    { h3Index: "8860145b27fffff", riskTier: "HIGH", score: 0.88 },
    { h3Index: "8860145b21fffff", riskTier: "HIGH", score: 0.82 },
    { h3Index: "8860145b25fffff", riskTier: "MEDIUM", score: 0.76 },
    { h3Index: "8860145b29fffff", riskTier: "MEDIUM", score: 0.69 },
    { h3Index: "8860145b2dfffff", riskTier: "LOW", score: 0.58 }
  ],
  explanation: [
    "Suspect SIM IMEI geofence matches Connaught Place corridor",
    "High velocity mule card withdrawals registered within 2.5km radius in past 48 hours",
    "Travel speed estimated at 22 km/h via urban arterial transit"
  ]
};

/**
 * Multiple alert scenarios for demonstration & testing alert transitions.
 */
export const mockMultipleAlerts = [
  mockActiveAlert,
  {
    alert_id: "ALT-CYBER-2026-092",
    case_id: "CASE-4402-SD",
    mule_account: "XXXX-XXXX-3341 (HDFC)",
    defrauded_amount: "₹ 3,40,000",
    incident_timestamp: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    origin_lat: 28.5494,
    origin_lng: 77.2536,
    risk_score: 0.96,
    withdrawal_window: {
      min: 10,
      max: 30
    },
    targets: [
      {
        id: "atm-south-01",
        name: "Axis Bank ATM - Nehru Place",
        type: "ATM",
        latitude: 28.5494,
        longitude: 77.2536,
        h3Index: "8860145a4bfffff",
        riskScore: 0.96,
        rank: 1,
        travelTime: "8 mins",
        address: "International Trade Tower, Nehru Place, New Delhi",
        expectedWindow: "10-25 mins",
        withdrawalProbability: "96%",
        riskTier: "CRITICAL"
      },
      {
        id: "branch-south-02",
        name: "ICICI Bank - Greater Kailash Branch",
        type: "Bank Branch",
        latitude: 28.5385,
        longitude: 77.2384,
        h3Index: "8860145a49fffff",
        riskScore: 0.89,
        rank: 2,
        travelTime: "14 mins",
        address: "M-Block Market, GK-I, New Delhi",
        expectedWindow: "15-30 mins",
        withdrawalProbability: "89%",
        riskTier: "HIGH"
      },
      {
        id: "bc-south-03",
        name: "Fino Payments BC Center - Kalkaji",
        type: "BC Point",
        latitude: 28.5422,
        longitude: 77.2612,
        h3Index: "8860145a47fffff",
        riskScore: 0.81,
        rank: 3,
        travelTime: "20 mins",
        address: "Main Market, Kalkaji, New Delhi",
        expectedWindow: "20-40 mins",
        withdrawalProbability: "81%",
        riskTier: "HIGH"
      }
    ],
    risk_cells: [
      { h3Index: "8860145a4bfffff", riskTier: "CRITICAL", score: 0.96 },
      { h3Index: "8860145a49fffff", riskTier: "HIGH", score: 0.89 },
      { h3Index: "8860145a47fffff", riskTier: "HIGH", score: 0.81 }
    ],
    explanation: [
      "Target ATM has highest density of rapid OTP-less cashout attempts",
      "Immediate proximity (800m) from suspect cellular BTS tower lock",
      "Mule account ATM card generated in nearby jurisdiction"
    ]
  }
];

export default mockLocations;

