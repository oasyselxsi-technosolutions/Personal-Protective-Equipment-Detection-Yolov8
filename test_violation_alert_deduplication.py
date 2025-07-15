import pytest
import redis
import time
from violation_alerts import is_duplicate_alert, get_redis_client

@pytest.fixture(scope="module")
def redis_client():
    """Fixture to provide a clean Redis client for testing."""
    try:
        client = get_redis_client(db=15)
        client.ping()  # Check if Redis is running
    except Exception:
        pytest.skip("Redis server is not running or not reachable on db=15")
    client.flushdb()
    try:
        yield client
    finally:
        client.flushdb()

def test_alert_deduplication(redis_client):
    """Test that duplicate alerts are detected within cooldown, and not after cooldown."""
    alert = {
        'type': 'No Helmet',
        'location': 'Zone A',
        'timestamp': '2025-07-14 10:00:00',
        'person_id': '123',
    }
    cooldown = 2  # seconds
    assert not is_duplicate_alert(alert, redis_client, cooldown=cooldown)
    assert is_duplicate_alert(alert, redis_client, cooldown=cooldown)
    time.sleep(cooldown + 1)
    assert not is_duplicate_alert(alert, redis_client, cooldown=cooldown)

def test_different_alerts_not_duplicate(redis_client):
    """Test that different alert types are not considered duplicates."""
    alert1 = {'type': 'No Helmet', 'location': 'Zone A', 'timestamp': '2025-07-14 10:00:00', 'person_id': '123'}
    alert2 = {'type': 'No Vest', 'location': 'Zone A', 'timestamp': '2025-07-14 10:00:00', 'person_id': '123'}
    cooldown = 5
    assert not is_duplicate_alert(alert1, redis_client, cooldown=cooldown)
    assert not is_duplicate_alert(alert2, redis_client, cooldown=cooldown)

def test_alerts_with_different_person_ids(redis_client):
    """Test that alerts for different person_ids are not considered duplicates."""
    alert1 = {'type': 'No Helmet', 'location': 'Zone A', 'timestamp': '2025-07-14 10:00:00', 'person_id': '123'}
    alert2 = {'type': 'No Helmet', 'location': 'Zone A', 'timestamp': '2025-07-14 10:00:00', 'person_id': '456'}
    cooldown = 5
    assert not is_duplicate_alert(alert1, redis_client, cooldown=cooldown)
    assert not is_duplicate_alert(alert2, redis_client, cooldown=cooldown)