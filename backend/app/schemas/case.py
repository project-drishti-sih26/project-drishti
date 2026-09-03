"""
FILE: backend/app/schemas/case.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    Pydantic schemas for the Case model. The Case represents a full fraud
    investigation record. These schemas define what the API accepts when
    creating a case and what it returns when fetching case details.

📌 WHAT TO IMPLEMENT HERE:

    1. CaseCreate (input when manually creating a case, if needed):
       class CaseCreate(BaseModel):
           victim_account_id: str
           flagged_mule_id: Optional[str] = None
           compromised_amount: float
           case_id: Optional[str] = None  # Auto-generated if not provided

    2. CaseResponse (what the GET /cases/{id} endpoint returns):
       class CaseResponse(BaseModel):
           case_id: str
           victim_account_id: str
           flagged_mule_id: Optional[str]
           compromised_amount: float
           status: str
           created_at: datetime
           prediction_payload: Optional[str]  # JSON string of ML prediction
           predicted_atm_rank1_id: Optional[str]

           class Config:
               from_attributes = True

    3. CaseStatusUpdate (PATCH body — for Role 4's Confirm/False Alarm buttons):
       class CaseStatusUpdate(BaseModel):
           status: str           # Must be one of: "INTERCEPTED", "MISSED", "FALSE_ALARM"
           officer_id: Optional[str] = None     # ID of officer who confirmed
           officer_notes: Optional[str] = None  # Optional notes
           confirmed_atm_id: Optional[str] = None  # Which ATM was it actually at?

           Add a Pydantic validator here to ensure status is one of the
           allowed values. Raise ValueError for invalid status strings.

    4. CaseList (for GET /cases — list all active cases):
       class CaseList(BaseModel):
           total: int
           cases: List[CaseResponse]

📌 HOW IT CONNECTS TO OTHER FILES:
    - api/endpoints/cases.py uses these schemas.
    - CaseStatusUpdate is the input to PATCH /cases/{case_id}/status.
    - The `status` updates written here become the ML retraining data later.
"""
