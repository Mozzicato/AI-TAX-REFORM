import pytest
import requests

def test_health_endpoint():
    response = requests.get('http://your-backend-url/health')
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}