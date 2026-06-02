export interface WeatherSummary {
  temperature: number;
  humidity: number;
  description: string;
}

export interface City {
  id: number;
  name: string;
  latest_weather: WeatherSummary | null;
}

export interface CreateCityResponse extends City {
  task_id: string;
}

export interface WeatherUpdateResponse {
  city_id: number;
  task_id: string;
  status: string;
}
