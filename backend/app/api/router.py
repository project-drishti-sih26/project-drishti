from fastapi import APIRouter
from app.api.endpoints import transactions, cases, locations

api_router = APIRouter()

api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])

# NOTE: the websocket router is deliberately NOT included here.
#
# It used to be mounted twice — once here (giving /api/v1/ws/alerts) and again in
# main.py (giving /ws/alerts). Two live URLs for the same endpoint is a real
# hazard, not just untidiness: the frontend connects to one of them, and anyone
# debugging a "dashboard not updating" problem can attach to the other, see
# traffic, and conclude the socket is fine. It is mounted once, in main.py, at
# /ws — which is also the conventional place for a transport that has no
# business carrying an API version prefix.
