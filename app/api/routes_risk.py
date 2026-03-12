from fastapi import APIRouter, HTTPException
from app.models.risk_models import RiskResponse
from app.services.risk_service import get_system_risk

router = APIRouter()

@router.get("/get_risk", response_model=RiskResponse)
async def get_risk():
    try:
        risk = get_system_risk()
        if risk < 0.3:
            status = "low"
        elif risk < 0.6:
            status = "moderate"
        elif risk < 0.8:
            status = "high"
        else:
            status = "critical"
        return RiskResponse(system_risk=risk, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_risk_history():
    """
    Return dummy historical risk data for the last 24 hours.
    Replace with real database query later.
    """
    import random
    import datetime
    now = datetime.datetime.now()
    data = []
    for i in range(24, 0, -1):
        data.append({
            "time": (now - datetime.timedelta(hours=i)).isoformat(),
            "risk": round(random.uniform(0.2, 0.8), 2)
        })
    return data
