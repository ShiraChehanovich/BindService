"""
The endpoint is configured with:
  FAIL_PROBABILITY    = 0.4  → 40 % of calls should fail
  TIMEOUT_PROBABILITY = 0.5  → 50 % of failures also sleep before failing
  TIMEOUT_SECONDS     = 10

asyncio.sleep is always mocked so tests never actually wait.
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app

# raise_server_exceptions=False → unhandled exceptions become HTTP 500
client = TestClient(app, raise_server_exceptions=False)

EXPECTED_FAIL_RATE = 0.4
TOLERANCE = 0.10   # acceptable deviation: ±10 percentage points
SAMPLE_SIZE = 300  # enough calls to make the rate statistically stable


# ---------------------------------------------------------------------------
# 1. Deterministic success: random always returns a value above FAIL_PROBABILITY
# ---------------------------------------------------------------------------
def test_bind_always_succeeds_when_random_above_threshold():
    """Endpoint must return 200 when no failure condition is triggered."""
    with patch("src.EntryPoint.controllers.bind.random.random", return_value=1.0):
        response = client.post("/bind")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 2. Deterministic failure: random always returns 0.0 (below every threshold)
# ---------------------------------------------------------------------------
def test_bind_always_fails_when_random_below_threshold():
    """
    Endpoint must return 500 when the failure condition is always triggered.
    asyncio.sleep is mocked so the test does not actually wait 10 s.
    """
    with patch("src.EntryPoint.controllers.bind.random.random", return_value=0.0), \
         patch("src.EntryPoint.controllers.bind.asyncio.sleep", new_callable=AsyncMock):
        response = client.post("/bind")

    assert response.status_code == 500


# ---------------------------------------------------------------------------
# 3. Probability test: observed failure rate must be close to FAIL_PROBABILITY
# ---------------------------------------------------------------------------
def test_bind_failure_rate_matches_configured_probability():
    """
    Over SAMPLE_SIZE calls the failure rate should be within
    EXPECTED_FAIL_RATE ± TOLERANCE (i.e. 30 %–50 %).
    asyncio.sleep is mocked so timeouts resolve instantly.
    """
    fail_count = 0

    with patch("src.EntryPoint.controllers.bind.asyncio.sleep", new_callable=AsyncMock):
        for _ in range(SAMPLE_SIZE):
            response = client.post("/bind")
            if response.status_code != 200:
                fail_count += 1

    observed_rate = fail_count / SAMPLE_SIZE
    low  = EXPECTED_FAIL_RATE - TOLERANCE
    high = EXPECTED_FAIL_RATE + TOLERANCE

    assert low <= observed_rate <= high, (
        f"Observed failure rate {observed_rate:.1%} is outside the expected "
        f"range [{low:.1%}, {high:.1%}] over {SAMPLE_SIZE} calls."
    )

