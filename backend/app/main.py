from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import City, WeatherData
from app.schemas import CityCreate, CityCreateResponse, CityRead, WeatherSummary, WeatherUpdateResponse
from app.tasks import update_weather_for_city

settings = get_settings()

app = FastAPI(title="Weather Enrichment Service", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _latest_weather(db: Session, city_id: int) -> WeatherSummary | None:
    weather = (
        db.query(WeatherData)
        .filter(WeatherData.city_id == city_id)
        .order_by(WeatherData.fetched_at.desc(), WeatherData.id.desc())
        .first()
    )
    if weather is None:
        return None
    return WeatherSummary(
        temperature=weather.temperature,
        humidity=weather.humidity,
        description=weather.description,
    )


def _city_to_read(db: Session, city: City) -> CityRead:
    return CityRead(id=city.id, name=city.name, latest_weather=_latest_weather(db, city.id))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/cities", response_model=CityCreateResponse, status_code=status.HTTP_201_CREATED)
def create_city(payload: CityCreate, db: Session = Depends(get_db)) -> CityCreateResponse:
    city = City(name=payload.name.strip())
    if not city.name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="City name cannot be blank")

    db.add(city)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="City already exists") from exc
    db.refresh(city)

    task = update_weather_for_city.delay(city.id)
    return CityCreateResponse(
        id=city.id,
        name=city.name,
        latest_weather=None,
        task_id=task.id,
    )


@app.get("/cities", response_model=list[CityRead])
def list_cities(db: Session = Depends(get_db)) -> list[CityRead]:
    cities = db.query(City).order_by(City.name.asc()).all()
    return [_city_to_read(db, city) for city in cities]


@app.post("/cities/{city_id}/update-weather", response_model=WeatherUpdateResponse, status_code=status.HTTP_202_ACCEPTED)
def manual_update_weather(city_id: int, db: Session = Depends(get_db)) -> WeatherUpdateResponse:
    city = db.get(City, city_id)
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    task = update_weather_for_city.delay(city.id)
    return WeatherUpdateResponse(city_id=city.id, task_id=task.id, status="queued")
