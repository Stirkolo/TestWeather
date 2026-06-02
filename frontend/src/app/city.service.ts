import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../environments/environment';
import { City, CreateCityResponse, WeatherUpdateResponse } from './city.model';

@Injectable({ providedIn: 'root' })
export class CityService {
  private readonly apiBaseUrl = environment.apiBaseUrl;

  constructor(private readonly http: HttpClient) {}

  listCities(): Observable<City[]> {
    return this.http.get<City[]>(`${this.apiBaseUrl}/cities`);
  }

  addCity(name: string): Observable<CreateCityResponse> {
    return this.http.post<CreateCityResponse>(`${this.apiBaseUrl}/cities`, { name });
  }

  updateWeather(cityId: number): Observable<WeatherUpdateResponse> {
    return this.http.post<WeatherUpdateResponse>(`${this.apiBaseUrl}/cities/${cityId}/update-weather`, {});
  }
}
