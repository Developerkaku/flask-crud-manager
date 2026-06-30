import pytest

from app import create_app, db as _db


@pytest.fixture
def app():
    application = create_app("testing")
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def _clean_db(app):
    """Ensure a fresh in-memory database for every test."""
    with app.app_context():
        _db.drop_all()
        _db.create_all()
    yield
