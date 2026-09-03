"""
FILE: backend/app/api/endpoints/cases.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file defines endpoints for managing Case records. Cases are created
    automatically by the trigger service, but officers need to:
    1. View active cases on the dashboard
    2. Mark cases as Intercepted/False Alarm (human-in-the-loop feedback)
    These endpoints power Role 4's frontend "Confirmed" and "False Alarm" buttons.

📌 WHAT TO IMPLEMENT HERE:

    router = APIRouter(prefix="/cases", tags=["Cases"])

    1. GET /cases — LIST ALL CASES (for dashboard):
       @router.get("/", response_model=CaseList)
       def get_cases(
           status: Optional[str] = None,   # Filter by "ACTIVE", "INTERCEPTED", etc.
           limit: int = 20,
           skip: int = 0,
           db: Session = Depends(get_db)
       ):
           """
           Fetch cases from DB, optionally filtered by status.
           Order by created_at descending (newest first).
           Used by Role 4's sidebar to show the live case list.
           """

    2. GET /cases/{case_id} — GET ONE CASE WITH FULL DETAILS:
       @router.get("/{case_id}", response_model=CaseResponse)
       def get_case(case_id: str, db: Session = Depends(get_db)):
           """
           Returns full case details including the prediction_payload JSON.
           Used when the frontend wants to show the full prediction breakdown
           for a selected case.
           Raise HTTPException(404) if not found.
           """

    3. PATCH /cases/{case_id}/status — UPDATE CASE OUTCOME (Human-in-the-loop):
       @router.patch("/{case_id}/status", response_model=CaseResponse)
       def update_case_status(
           case_id: str,
           update: CaseStatusUpdate,
           db: Session = Depends(get_db)
       ):
           """
           This is the HUMAN-IN-THE-LOOP endpoint.
           Called when the police officer clicks:
           - ✅ "Confirmed Interception" → status = "INTERCEPTED"
           - ❌ "False Alarm" → status = "FALSE_ALARM"
           - 📍 "Missed" → status = "MISSED"

           Steps:
           1. Fetch the case by case_id. Raise 404 if not found.
           2. Validate that the new status is valid.
           3. Update: case.status = update.status
           4. Optionally store officer_notes in the case.
           5. Commit and return the updated case.

           WHY IS THIS IMPORTANT?
           The outcome stored here (INTERCEPTED vs MISSED vs FALSE_ALARM)
           becomes the ground truth label for ML model retraining.
           - If Rank #1 ATM prediction was INTERCEPTED → that's a True Positive.
           - If prediction was FALSE_ALARM → that helps identify model bias.
           """

📌 HOW IT CONNECTS TO OTHER FILES:
    - schemas/case.py provides CaseResponse, CaseList, CaseStatusUpdate.
    - models/case.py provides the Case ORM model.
    - Registered in api/router.py with prefix /cases.
    - Role 4's frontend calls PATCH /cases/{id}/status when officer clicks feedback buttons.
"""
