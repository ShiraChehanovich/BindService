import random
import asyncio
from fastapi import APIRouter, HTTPException

router = APIRouter()

FAIL_PROBABILITY = 0.4
TIMEOUT_PROBABILITY = 0.5
TIMEOUT_SECONDS = 10


@router.post("/bind")
async def bind():
    if random.random() < FAIL_PROBABILITY:
        if random.random() < TIMEOUT_PROBABILITY:
            await asyncio.sleep(TIMEOUT_SECONDS)
        raise HTTPException(status_code=500, detail="Random failure")

    return {"status": "ok"}