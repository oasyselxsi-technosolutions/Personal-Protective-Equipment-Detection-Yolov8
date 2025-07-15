# test_flask_violation_alert.py
import pytest
from flaskapp import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

from unittest.mock import patch

@patch('flaskapp.send_sms')
@patch('flaskapp.send_email')
def test_violation_alert_api(mock_send_email, mock_send_sms, client):
    response = client.post('/api/violation_alert', json={
        'type': 'No Helmet',
        'location': 'Zone A',
        'timestamp': '2025-07-14T12:00:00Z'
    })
    assert response.status_code == 200
    # Accept either key depending on your API response
    assert response.json.get('alert') in ('sent', 'suppressed')