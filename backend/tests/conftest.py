import pytest

@pytest.fixture(scope='session')
def client():
    from backend import create_app
    app = create_app()
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def run_around_tests(client):
    pass