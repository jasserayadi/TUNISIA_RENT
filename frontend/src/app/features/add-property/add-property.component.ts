import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Router, RouterLink,  } from '@angular/router';
import { PropertyCreate } from '../../core/models/property.model';
import { PropertyService } from '../../core/services/property.service';

@Component({
  selector: 'app-add-property',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './add-property.component.html',
  styleUrls: ['./add-property.component.scss']
})
export class AddPropertyComponent {
  form: FormGroup;
  loading = false;
  success = false;
  error: string | null = null;

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

  amenities = [
    { key: 'is_house', label: 'House' },
    { key: 'furnished', label: 'Furnished' },
    { key: 'parking', label: 'Parking' },
    { key: 'elevator', label: 'Elevator' },
    { key: 'aircon', label: 'Air Conditioning' },
    { key: 'heating', label: 'Heating' },
    { key: 'security', label: 'Security' },
    { key: 'pool', label: 'Pool' },
    { key: 'sea_view', label: 'Sea View' },
    { key: 'terrace', label: 'Terrace' },
    { key: 'equipped_kitchen', label: 'Equipped Kitchen' }
  ];

  get availableCities(): string[] {
    const gov = this.form.get('governorate')?.value;
    return this.citiesByGovernorate[gov] ?? [];
  }

  constructor(
    private fb: FormBuilder,
    private propertyService: PropertyService,
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
      rent: [950, [Validators.required, Validators.min(1)]],

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
      equipped_kitchen: [false]
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
    this.success = false;

    const raw = this.form.value;
    const payload: PropertyCreate = {
      governorate: raw.governorate,
      city: raw.city,
      surface: Number(raw.surface),
      bedrooms: Number(raw.bedrooms),
      bathrooms: Number(raw.bathrooms),
      floor: raw.floor !== null && raw.floor !== '' ? Number(raw.floor) : null,
      condition: raw.condition,
      rent: Number(raw.rent),
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
      equipped_kitchen: raw.equipped_kitchen
    };

    this.propertyService.create(payload).subscribe({
      next: (created) => {
        this.loading = false;
        this.success = true;
        // Redirect after a short delay so the user sees the confirmation
        setTimeout(() => this.router.navigate(['/properties']), 1200);
        console.log('Created property id =', created.id);
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail ?? 'Could not create property.';
      }
    });
  }
}