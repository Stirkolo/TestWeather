from __future__ import annotations

from dataclasses import dataclass

import requests

from app.config import get_settings


WEATHER_CODE_DESCRIPTIONS = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    95: "thunderstorm",
}


@dataclass(frozen=True)
class WeatherResult:
    temperature: float
    humidity: int
    description: str
    raw_payload: dict


class WeatherLookupError(RuntimeError):
    pass


def fetch_weather_for_city(city_name: str) -> WeatherResult:
    """Fetch current weather from Open-Meteo, a public weather API requiring no key."""
    timeout = get_settings().weather_request_timeout_seconds
    geo_response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city_name, "count": 1, "language": "en", "format": "json"},
        timeout=timeout,
    )
    geo_response.raise_for_status()
    geo_payload = geo_response.json()
    results = geo_payload.get("results") or []
    if not results:
        raise WeatherLookupError(f"City not found by weather provider: {city_name}")

    location = results[0]
    forecast_response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "temperature_2m,relative_humidity_2m,weather_code",
            "timezone": "auto",
        },
        timeout=timeout,
    )
    forecast_response.raise_for_status()
    forecast_payload = forecast_response.json()
    current = forecast_payload.get("current") or {}
    if "temperature_2m" not in current or "relative_humidity_2m" not in current:
        raise WeatherLookupError(f"Weather provider returned incomplete data for: {city_name}")

    weather_code = current.get("weather_code")
    description = WEATHER_CODE_DESCRIPTIONS.get(weather_code, f"weather code {weather_code}")
    return WeatherResult(
        temperature=float(current["temperature_2m"]),
        humidity=int(current["relative_humidity_2m"]),
        description=description,
        raw_payload={"geocoding": geo_payload, "forecast": forecast_payload},
    )
