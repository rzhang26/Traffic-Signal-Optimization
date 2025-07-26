from fastapi import APIRouter, HTTPException
from app.services.data_fetcher import fetch_incidents 
from app.services.data_cleaner import clean_incidents

router = APIRouter()

@router.get("/trends")
async def get_trends(county: str, month: str):
    try:
        raw = fetch_incidents(county)
        df = clean_incidents(raw)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
    return {
        "count": len(df),
        "incidents": df.head(10).to_dict(orient="records")
    }
    
