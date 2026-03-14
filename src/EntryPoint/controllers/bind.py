import random
import asyncio
from fastapi import APIRouter

from src.Common.Exceptions import TimeoutException
from src.Common.Utiles.config import FAIL_PROBABILITY, TIMEOUT_PROBABILITY, TIMEOUT_SECONDS

router = APIRouter()


@router.post("/bind")
async def bind():
    if random.random() < FAIL_PROBABILITY:
        if random.random() < TIMEOUT_PROBABILITY:
            await asyncio.sleep(TIMEOUT_SECONDS)
        raise TimeoutException
    return
