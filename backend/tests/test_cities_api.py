from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import City, WeatherData


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_city_persists_city_and_enqueues_weather_task(client, db_session, monkeypatch):
    queued = []

    def fake_delay(city_id):
        queued.append(city_id)
        return SimpleNamespace(id="task-123")

    monkeypatch.setattr("app.main.update_weather_for_city.delay", fake_delay)

    response = client.post("/cities", json={"name": "Kyiv"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Kyiv"
    assert body["latest_weather"] is None
    assert body["task_id"] == "task-123"

    saved_city = db_session.query(City).one()
    assert saved_city.name == "Kyiv"
    assert queued == [saved_city.id]


def test_list_cities_returns_latest_weather_for_each_city(client, db_session):
    city = City(name="Lviv")
    db_session.add(city)
    db_session.flush()
    db_session.add_all([
        WeatherData(
            city_id=city.id,
            temperature=12.3,
            humidity=60,
            description="old rain",
            fetched_at=datetime.now(timezone.utc) - timedelta(hours=2),
        ),
        WeatherData(
            city_id=city.id,
            temperature=17.8,
            humidity=51,
            description="clear sky",
            fetched_at=datetime.now(timezone.utc),
        ),
    ])
    db_session.commit()

    response = client.get("/cities")

    assert response.status_code == 200
    body = response.json()
    assert body == [
        {
            "id": city.id,
            "name": "Lviv",
            "latest_weather": {
                "temperature": 17.8,
                "humidity": 51,
                "description": "clear sky",
            },
        }
    ]


def test_manual_update_weather_enqueues_task_for_existing_city(client, db_session, monkeypatch):
    city = City(name="Odesa")
    db_session.add(city)
    db_session.commit()
    queued = []

    def fake_delay(city_id):
        queued.append(city_id)
        return SimpleNamespace(id="manual-456")

    monkeypatch.setattr("app.main.update_weather_for_city.delay", fake_delay)

    response = client.post(f"/cities/{city.id}/update-weather")

    assert response.status_code == 202
    assert response.json() == {
        "city_id": city.id,
        "task_id": "manual-456",
        "status": "queued",
    }
    assert queued == [city.id]


def test_manual_update_weather_returns_404_for_unknown_city(client):
    response = client.post("/cities/999/update-weather")

    assert response.status_code == 404
    assert response.json()["detail"] == "City not found"
