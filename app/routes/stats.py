from fastapi import APIRouter, HTTPException

from model_schema.schemas import StatsResponse
from db_store.stats_store import get_stats

router = APIRouter(tags=["stats"])


@router.get("/stats/{bot_id}", response_model=StatsResponse)
async def get_bot_stats(bot_id: str) -> StatsResponse:
   
    stats = await get_stats(bot_id)

    if stats["total_messages"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No stats found for bot_id '{bot_id}'. "
                   "Either the bot doesn't exist or no chat has occurred yet."
        )

    return StatsResponse(**stats)
