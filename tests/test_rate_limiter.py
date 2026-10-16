from concurrent.futures import ThreadPoolExecutor

import pytest
import rate_limiter


@pytest.fixture(autouse=True)
def reset_limiter():
    # Start every test with empty request histories
    with rate_limiter.lock:
        rate_limiter.requests.clear()

    yield

    with rate_limiter.lock:
        rate_limiter.requests.clear()


def test_first_five_requests_allowed():
    results = [
        rate_limiter.is_allowed("hospital_a")
        for _ in range(5)
    ]

    assert results == [True] * 5


def test_sixth_request_rejected():
    for _ in range(5):
        rate_limiter.is_allowed("hospital_a")

    assert rate_limiter.is_allowed("hospital_a") is False


def test_hospitals_have_independent_limits():
    for _ in range(5):
        rate_limiter.is_allowed("hospital_a")

    assert rate_limiter.is_allowed("hospital_a") is False
    assert rate_limiter.is_allowed("hospital_b") is True


def test_concurrent_requests():
    # Send 20 requests from different threads
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(
            executor.map(
                rate_limiter.is_allowed,
                ["hospital_a"] * 20
            )
        )

    assert results.count(True) == 5
    assert results.count(False) == 15