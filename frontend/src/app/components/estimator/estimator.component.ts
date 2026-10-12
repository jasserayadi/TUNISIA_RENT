import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  ApiService,
  PredictRequest,
  PredictResponse,
} from '../../core/services/api.service';

@Component({
  selector: 'app-estimator',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './estimator.component.html',
  styleUrl: './estimator.component.css',
})
export class EstimatorComponent {
  form: PredictRequest = {
    governorate: 'Tunis',
    city: 'La Marsa',
    quartier: 'La Marsa Ville',
    surface: 120,
    bedrooms: 2,
    bathrooms: 2,
    is_house: 0,
    furnished: 1,
    garage: 1,
    elevator: 1,
    aircon: 1,
    heating: 1,
    security: 1,
    pool: 0,
    sea_view: 0,
    terrace: 1,
    equipped_kitchen: 1,
    advertised_price: null,
  };

  result  = signal<PredictResponse | null>(null);
  loading = signal(false);
  error   = signal<string | null>(null);

  // Auto-filled suggestions per governorate
  readonly citiesByGovernorate: Record<string, string[]> = {
    Tunis:     ['Tunis', 'La Marsa', 'Carthage', 'Le Kram', 'La Goulette'],
    Ariana:    ['Ariana', 'La Soukra', 'Raoued', 'Mnihla'],
    'Ben arous': ['Ben arous', 'El Mourouj', 'Hammam Lif', 'Ezzahra', 'Radès'],
    Nabeul:    ['Nabeul', 'Hammamet', 'Kélibia', 'Korba', 'Soliman'],
    Sousse:    ['Sousse', 'Hammam Sousse', 'Akouda', 'Khezama'],
    Sfax:      ['Sfax', 'Sfax Sud', 'Sakiet Ezzit', 'Menzel Chaker'],
    'La manouba': ['La Manouba', 'Douar Hicher', 'Oued Ellil', 'Mornaguia'],
    Monastir:  ['Monastir', 'Ksar Hellal', 'Moknine'],
    Bizerte:   ['Bizerte', 'Menzel Bourguiba', 'Mateur'],
    Mahdia:    ['Mahdia', 'Ksour Essef', 'Chebba'],
    Gabès:     ['Gabès', 'Gabès Ville', 'El Hamma'],
  };

  get availableCities(): string[] {
    return this.citiesByGovernorate[this.form.governorate] ?? [this.form.city];
  }

  constructor(private api: ApiService) {}

  submit() {
    this.loading.set(true);
    this.error.set(null);
    this.result.set(null);

    // Strip empty advertised_price
    const body: PredictRequest = { ...this.form };
    if (!body.advertised_price || body.advertised_price <= 0) {
      delete body.advertised_price;
    }

    this.api.predict(body).subscribe({
      next: (r) => {
        this.result.set(r);
        this.loading.set(false);
      },
      error: (e) => {
        console.error(e);
        this.error.set(
          e?.error?.detail
            ? JSON.stringify(e.error.detail)
            : 'Could not reach the API. Is the backend running?'
        );
        this.loading.set(false);
      },
    });
  }

  reset() {
    this.result.set(null);
    this.error.set(null);
  }
}