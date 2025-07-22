from fastapi import APIRouter

router = APIRouter()

@router.get("/trends")
async def get_trends(county: str, month: str):
    """
    Placeholder endpoint. Will fetch & clean data before returning results.
    """
    return {"message": f"Trends for {county} in {month} is working!"}
    
