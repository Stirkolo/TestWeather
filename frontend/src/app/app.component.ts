import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';

import { City } from './city.model';
import { CityService } from './city.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  private readonly cityService = inject(CityService);
  private readonly fb = inject(FormBuilder);

  cities: City[] = [];
  isLoading = false;
  isAdding = false;
  errorMessage = '';
  successMessage = '';
  updatingCityIds = new Set<number>();

  cityForm = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.maxLength(255)]],
  });


  ngOnInit(): void {
    this.loadCities();
  }

  loadCities(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.cityService
      .listCities()
      .pipe(finalize(() => (this.isLoading = false)))
      .subscribe({
        next: (cities) => (this.cities = cities),
        error: () => (this.errorMessage = 'Unable to load cities. Check that the backend is running.'),
      });
  }

  addCity(): void {
    if (this.cityForm.invalid) {
      this.cityForm.markAllAsTouched();
      return;
    }

    const name = this.cityForm.controls.name.value.trim();
    if (!name) {
      this.cityForm.controls.name.setErrors({ required: true });
      return;
    }

    this.isAdding = true;
    this.errorMessage = '';
    this.successMessage = '';
    this.cityService
      .addCity(name)
      .pipe(finalize(() => (this.isAdding = false)))
      .subscribe({
        next: (city) => {
          this.successMessage = `${city.name} added. Weather enrichment task queued.`;
          this.cityForm.reset();
          this.loadCities();
        },
        error: (error) => {
          this.errorMessage = error?.error?.detail ?? 'Unable to add city.';
        },
      });
  }

  updateWeather(city: City): void {
    this.updatingCityIds.add(city.id);
    this.errorMessage = '';
    this.successMessage = '';
    this.cityService
      .updateWeather(city.id)
      .pipe(finalize(() => this.updatingCityIds.delete(city.id)))
      .subscribe({
        next: () => {
          this.successMessage = `Weather update queued for ${city.name}. Refresh in a moment to see new data.`;
          this.loadCities();
        },
        error: () => (this.errorMessage = `Unable to update weather for ${city.name}.`),
      });
  }

  isUpdating(cityId: number): boolean {
    return this.updatingCityIds.has(cityId);
  }
}
