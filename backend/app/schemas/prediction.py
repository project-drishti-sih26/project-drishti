"""
FILE: backend/app/schemas/prediction.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file defines the Pydantic schema for the ML prediction output payload.
    This is THE most important data structure in the entire system —
    it is the JSON object that flows from the ML Engine → Backend → WebSocket
    → Frontend (Roles 3 & 4) → Police Dispatch PDF.
    ALL teams must agree on this contract. Do NOT change it without
    coordinating with the Frontend team.

📌 WHY IS THIS FILE NEEDED?
    The ML engine (Role 2) and the WebSocket broadcaster (Role 1) must speak
    the same language. By defining this Pydantic schema:
    - The ML engine's output gets auto-validated before being broadcast.
    - The Frontend team has a guaranteed, documented JSON structure to build against.
    - FastAPI's /docs Swagger UI shows a clear example of the prediction payload.

📌 WHAT TO IMPLEMENT HERE:

    1. ATMCandidate schema (one ranked ATM in the Top-5 list):
       class ATMCandidate(BaseModel):
           rank: int                    # 1 to 5
           location_id: str            # e.g., "ATM_SBI_CONNAUGHT_001"
           bank_name: str              # e.g., "State Bank of India"
           latitude: float             # For Mapbox marker placement
           longitude: float            # For Mapbox marker placement
           address: str                # For Police Dispatch PDF
           distance_km: float          # Road distance from mule's last known position
           travel_time_mins: float     # Estimated travel time by road
           confidence_score: float     # ML model score (0.0 to 1.0)
           explanation: str            # SHAP-generated natural language reason
                                       # e.g., "High fraud density (6 incidents) + 7-min road travel"

    2. PredictionTimeWindow schema:
       class PredictionTimeWindow(BaseModel):
           start: datetime             # e.g., "2026-09-03T20:12:00Z"
           end: datetime               # e.g., "2026-09-03T20:28:00Z"
           minutes_from_now: int       # e.g., 27 — used for frontend countdown timer
           confidence: float           # 0.0 to 1.0 (Survival Analysis confidence)

    3. PredictionAlert (THE MAIN PAYLOAD — broadcast over WebSocket):
       class PredictionAlert(BaseModel):
           alert_id: str               # Unique alert ID: "ALERT-2026-09-03-001"
           case_id: str                # Links to the Case in the DB
           mule_account_id: str        # The mule account that received the trigger transaction
           victim_account_id: str      # The victim's account
           compromised_amount: float   # ₹ stolen
           detected_at: datetime       # When the trigger fired
           time_window: PredictionTimeWindow
           top_5_atms: List[ATMCandidate]  # Exactly 5 ranked candidates
           model_used: str             # "LambdaMART" or "FallbackHeuristic" (for transparency)
           total_candidates_evaluated: int  # How many ATMs were considered (e.g., 187)

    4. CaseStatusUpdate (INPUT schema for PATCH /cases/{case_id}):
       class CaseStatusUpdate(BaseModel):
           status: str  # "INTERCEPTED", "MISSED", "FALSE_ALARM"
           officer_notes: Optional[str] = None  # Free text for police officer

📌 HOW IT CONNECTS TO OTHER FILES:
    - ml_engine/pipelines/inference_pipeline.py returns a dict matching
      this schema's structure. Backend validates it here before broadcasting.
    - services/alert_service.py creates a `PredictionAlert` object and
      calls the WebSocket broadcaster.
    - api/endpoints/websockets.py sends `PredictionAlert.model_dump_json()`
      over the ws:// connection to all connected Frontend clients.
    - Frontend (Role 3 & 4) parses this exact JSON structure to populate
      the Mapbox markers and the Top-5 ATM sidebar cards.

📌 LIBRARIES TO USE:
    - pydantic (BaseModel)
    - typing (List, Optional)
    - datetime (datetime)
"""
