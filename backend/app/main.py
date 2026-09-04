from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import create_access_token, Token, MOCK_USERS_DB
from app.api.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set at startup so /health can report whether the real ML engine is live rather
# than leaving the team to discover it from a degraded alert mid-demo.
ML_ENGINE_STATUS = {"ready": False, "detail": "not initialised"}


def _warm_ml_engine() -> None:
    """
    Loads every ML artefact and runs one throwaway prediction at boot.

    WHY THIS EXISTS
    ---------------
    The first live request otherwise pays for all of it at once: the LightGBM
    booster, the Cox PH pickle, the feature store, the H3 tables, the ATM CSV,
    and SHAP's TreeExplainer construction. Measured cold start was 13.5 seconds.

    The product's entire claim is a sub-2-second alert inside a ~14-minute
    interception window, so a 13-second first alert is not a cosmetic problem —
    it is the demo, and it is the one request that will be timed. Paying that
    cost at boot makes the first real alert as fast as the hundredth.

    Importing ml_engine here also applies its console-encoding guard before any
    request can hit it, and surfaces a missing dependency in the startup log
    instead of as a silent fallback to the degraded heuristic.
    """
    global ML_ENGINE_STATUS
    import time
    from datetime import datetime, timezone

    t0 = time.time()
    try:
        from ml_engine.pipelines.inference_pipeline import predict_fraud_cashout

        result = predict_fraud_cashout({
            "mule_account_id": "__WARMUP__",
            "victim_account_id": "__WARMUP__",
            "last_latitude": 28.6139,
            "last_longitude": 77.2090,
            "transaction_amount": 100000.0,
            "transaction_timestamp": datetime.now(timezone.utc).isoformat(),
            "case_id": "WARMUP",
            "mule_tier": 1,
        })
        elapsed = time.time() - t0
        model = result.get("model_used")
        if model == "LambdaMART":
            ML_ENGINE_STATUS = {
                "ready": True,
                "detail": f"LambdaMART + {result['time_window']['model_source']} warm",
                "warmup_seconds": round(elapsed, 2),
                "candidates_indexed": result.get("total_candidates_evaluated"),
                "scorecard": result.get("model_scorecard", {}),
            }
            print(f"[Startup] ML engine warm in {elapsed:.2f}s | ranker={model} | "
                  f"{result.get('total_candidates_evaluated')} cash points indexed")
        else:
            ML_ENGINE_STATUS = {
                "ready": False,
                "detail": f"Ranker degraded to {model} - alerts will be flagged degraded",
                "warmup_seconds": round(elapsed, 2),
            }
            print(f"[Startup] WARNING: ranker is {model}, not the trained LambdaMART. "
                  f"Run: python ml_engine/train_models.py")
    except Exception as e:
        ML_ENGINE_STATUS = {"ready": False, "detail": f"{type(e).__name__}: {e}"}
        print(f"[Startup] ML ENGINE UNAVAILABLE: {type(e).__name__}: {e}")
        print("[Startup] Alerts will use the DEGRADED heuristic and be flagged as such.")


@app.on_event("startup")
def on_startup():
    # Ensure all ORM models are registered with Base before creating tables
    from app.models.account import Account
    from app.models.transaction import Transaction
    from app.models.case import Case
    from app.models.location import PhysicalLocation
    Base.metadata.create_all(bind=engine)

    _warm_ml_engine()


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "Project Drishti API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    """
    Readiness probe. Reports ML engine state explicitly so that "the API is up"
    is never mistaken for "the API can predict" — the two failed independently
    during development and the difference is what decides whether an alert is
    real or a flagged fallback.
    """
    from app.services.alert_service import manager
    return {
        "status": "healthy",
        "ml_engine": ML_ENGINE_STATUS,
        "websocket": manager.stats(),
    }


@app.post("/api/v1/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = MOCK_USERS_DB.get(form_data.username)
    if not user or user["hashed_password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


from app.api.endpoints import websockets

app.include_router(api_router, prefix="/api/v1")
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])
