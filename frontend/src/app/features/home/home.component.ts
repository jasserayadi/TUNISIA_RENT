import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { PredictRequest } from '../../core/models/prediction.model';
import { PredictionService } from '../../core/services/prediction.service';
import { RevealDirective } from '../../shared/reveal.directive';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, RevealDirective],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {
  form: FormGroup;
  loading = false;
  error: string | null = null;

  locations = [
    { city: 'La Marsa', gov: 'Tunis', image: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80', listings: 42, avgRent: 1400 },
    { city: 'Ariana Ville', gov: 'Ariana', image: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80', listings: 38, avgRent: 950 },
    { city: 'Djerba', gov: 'Medenine', image: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80', listings: 27, avgRent: 720 },
    { city: 'Hammamet', gov: 'Nabeul', image: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80', listings: 31, avgRent: 880 },
    { city: 'Sousse Ville', gov: 'Sousse', image: 'https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=800&q=80', listings: 24, avgRent: 810 },
    { city: 'Gammarth', gov: 'Tunis', image: 'https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=800&q=80', listings: 18, avgRent: 1900 }
  ];

  governorates = [
    'Ariana', 'Ben Arous', 'Bizerte', 'Gabes', 'Gafsa', 'Jendouba',
    'Kairouan', 'Kasserine', 'Kebili', 'Kef', 'Mahdia', 'Manouba',
    'Medenine', 'Monastir', 'Nabeul', 'Sfax', 'Sidi Bouzid',
    'Siliana', 'Sousse', 'Tataouine', 'Tozeur', 'Tunis', 'Zaghouan'
  ];

  citiesByGovernorate: Record<string, string[]> = {
    'Ariana': ['Ariana Ville', 'Raoued', 'Soukra', 'Borj Louzir'],
    'Ben Arous': ['Ben Arous', 'Ezzahra', 'Hammam Lif', 'Radès'],
    'Tunis': ['Tunis Centre', 'Bab Bhar', 'El Menzah', 'El Manar', 'La Marsa', 'Carthage', 'Gammarth'],
    'Nabeul': ['Nabeul', 'Hammamet', 'Kelibia', 'Korba'],
    'Sousse': ['Sousse Ville', 'Khezama', 'Hammam Sousse', 'Msaken'],
    'Monastir': ['Monastir', 'Skanes', 'Sahline'],
    'Sfax': ['Sfax Ville', 'Sakiet Ezzit', 'Sakiet Eddaier'],
    'Bizerte': ['Bizerte', 'Menzel Bourguiba', 'Ras Jebel'],
    'Medenine': ['Djerba', 'Medenine', 'Zarzis'],
    'Gabes': ['Gabes', 'Mareth', 'Ghannouch']
  };

  conditions = [
    { value: 'excellent', label: 'Excellent' },
    { value: 'good', label: 'Good' },
    { value: 'average', label: 'Average' },
    { value: 'needs_work', label: 'Needs Work' }
  ];

  get availableCities(): string[] {
    const gov = this.form.get('governorate')?.value;
    return this.citiesByGovernorate[gov] ?? [];
  }

  constructor(
    private fb: FormBuilder,
    private predictionService: PredictionService,
    private router: Router
  ) {
    this.form = this.fb.group({
      governorate: ['Ariana', Validators.required],
      city: ['Ariana Ville', Validators.required],
      surface: [90, [Validators.required, Validators.min(1), Validators.max(2000)]],
      bedrooms: [2, [Validators.required, Validators.min(1), Validators.max(15)]],
      bathrooms: [1, [Validators.required, Validators.min(1), Validators.max(10)]],
      floor: [2],
      condition: ['good'],
      is_house: [false],
      furnished: [false],
      parking: [true],
      elevator: [false],
      aircon: [false],
      heating: [false],
      security: [false],
      pool: [false],
      sea_view: [false],
      terrace: [false],
      equipped_kitchen: [false],
      advertised_price: [null]
    });

    this.form.get('governorate')?.valueChanges.subscribe((gov) => {
      const cities = this.citiesByGovernorate[gov] ?? [];
      this.form.get('city')?.setValue(cities[0] ?? '');
    });
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.loading = true;
    this.error = null;

    const raw = this.form.value;
    const payload: PredictRequest = {
      governorate: raw.governorate,
      city: raw.city,
      surface: Number(raw.surface),
      bedrooms: Number(raw.bedrooms),
      bathrooms: Number(raw.bathrooms),
      is_house: raw.is_house,
      furnished: raw.furnished,
      parking: raw.parking,
      elevator: raw.elevator,
      aircon: raw.aircon,
      heating: raw.heating,
      security: raw.security,
      pool: raw.pool,
      sea_view: raw.sea_view,
      terrace: raw.terrace,
      equipped_kitchen: raw.equipped_kitchen,
      advertised_price: raw.advertised_price ? Number(raw.advertised_price) : null
    };

    this.predictionService.predict(payload).subscribe({
      next: (response) => {
        this.loading = false;
        this.router.navigate(['/result'], { state: { prediction: response, request: payload } });
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail ?? 'Prediction failed. Please try again.';
      }
    });
  }
}