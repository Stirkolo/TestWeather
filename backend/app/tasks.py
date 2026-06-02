from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import City, WeatherData
from app.weather_client import fetch_weather_for_city


@celery_app.task(name="app.tasks.update_weather_for_city", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def update_weather_for_city(city_id: int) -> dict:
    db = SessionLocal()
    try:
        city = db.get(City, city_id)
        if city is None:
            return {"status": "not_found", "city_id": city_id}

        weather = fetch_weather_for_city(city.name)
        weather_record = WeatherData(
            city_id=city.id,
            temperature=weather.temperature,
            humidity=weather.humidity,
            description=weather.description,
            raw_payload=weather.raw_payload,
        )
        db.add(weather_record)
        db.commit()
        return {"status": "updated", "city_id": city.id, "weather_id": weather_record.id}
    finally:
        db.close()
