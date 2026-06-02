from pydantic import BaseModel, ConfigDict, Field


class CityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class WeatherSummary(BaseModel):
    temperature: float
    humidity: int
    description: str


class CityRead(BaseModel):
    id: int
    name: str
    latest_weather: WeatherSummary | None = None

    model_config = ConfigDict(from_attributes=True)


class CityCreateResponse(CityRead):
    task_id: str


class WeatherUpdateResponse(BaseModel):
    city_id: int
    task_id: str
    status: str = "queued"
