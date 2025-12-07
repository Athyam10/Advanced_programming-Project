import pytest

import pytest


@pytest.fixture
def app():
    from app import create_app, db
    from app.models import Book

    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        b = Book(title='Test', author='Author')
        db.session.add(b)
        db.session.commit()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_health(client):
    res = client.get('/health')
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_books(client):
    res = client.get('/books')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert data and data[0]['title'] == 'Test'
