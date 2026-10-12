import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Property } from '../../core/models/property.model';
import { PropertyService } from '../../core/services/property.service';
import { RevealDirective } from '../../shared/reveal.directive';

interface Filters {
  governorate: string;
  city: string;
  min_rent: number | null;
  max_rent: number | null;
  min_surface: number | null;
  max_surface: number | null;
  bedrooms: number | null;
  furnished: boolean | null;
  parking: boolean | null;
  elevator: boolean | null;
  aircon: boolean | null;
  heating: boolean | null;
  security: boolean | null;
  pool: boolean | null;
  sea_view: boolean | null;
  terrace: boolean | null;
  equipped_kitchen: boolean | null;
  is_house: boolean | null;
}

@Component({
  selector: 'app-properties-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, RevealDirective],
  templateUrl: './properties-list.component.html',
  styleUrls: ['./properties-list.component.scss']
})
export class PropertiesListComponent implements OnInit {
  properties: Property[] = [];
  loading = false;
  error: string | null = null;
  showAdvanced = false;

  governorates = [
    'Ariana', 'Ben Arous', 'Bizerte', 'Gabes', 'Gafsa', 'Jendouba',
    'Kairouan', 'Kasserine', 'Kebili', 'Kef', 'Mahdia', 'Manouba',
    'Medenine', 'Monastir', 'Nabeul', 'Sfax', 'Sidi Bouzid',
    'Siliana', 'Sousse', 'Tataouine', 'Tozeur', 'Tunis', 'Zaghouan'
  ];

  /** Tri-state amenity toggles: null = ignore, true = must have, false = must not have */
  amenityToggles: { key: keyof Filters; label: string }[] = [
    { key: 'furnished', label: 'Furnished' },
    { key: 'parking', label: 'Parking' },
    { key: 'elevator', label: 'Elevator' },
    { key: 'aircon', label: 'Air Conditioning' },
    { key: 'heating', label: 'Heating' },
    { key: 'security', label: 'Security' },
    { key: 'pool', label: 'Pool' },
    { key: 'sea_view', label: 'Sea View' },
    { key: 'terrace', label: 'Terrace' },
    { key: 'equipped_kitchen', label: 'Equipped Kitchen' },
    { key: 'is_house', label: 'House (not apartment)' }
  ];

  filters: Filters = this.emptyFilters();

  constructor(private propertyService: PropertyService) {}

  ngOnInit(): void {
    this.load();
  }

  emptyFilters(): Filters {
    return {
      governorate: '',
      city: '',
      min_rent: null,
      max_rent: null,
      min_surface: null,
      max_surface: null,
      bedrooms: null,
      furnished: null,
      parking: null,
      elevator: null,
      aircon: null,
      heating: null,
      security: null,
      pool: null,
      sea_view: null,
      terrace: null,
      equipped_kitchen: null,
      is_house: null
    };
  }

  load(): void {
    this.loading = true;
    this.error = null;

    const params: Record<string, any> = {};
    Object.entries(this.filters).forEach(([k, v]) => {
      if (v !== null && v !== '' && v !== undefined) {
        params[k] = v;
      }
    });

    this.propertyService.list(params).subscribe({
      next: (data) => {
        this.properties = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'Could not load properties.';
        this.loading = false;
      }
    });
  }

  reset(): void {
    this.filters = this.emptyFilters();
    this.load();
  }

  /** Cycle: null → true → false → null */
  cycleToggle(key: keyof Filters): void {
    const current = this.filters[key] as boolean | null;
    if (current === null) this.filters[key] = true as never;
    else if (current === true) this.filters[key] = false as never;
    else this.filters[key] = null as never;
  }

  toggleState(key: keyof Filters): 'any' | 'yes' | 'no' {
    const v = this.filters[key] as boolean | null;
    return v === null ? 'any' : v ? 'yes' : 'no';
  }

  activeFilterCount(): number {
    return Object.values(this.filters).filter(
      (v) => v !== null && v !== '' && v !== undefined
    ).length;
  }

  /** Pick a curated Unsplash photo based on the property features. */
  imageFor(p: Property): string {
    const byFeature: Record<string, string[]> = {
      sea: [
        'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=800&q=80'
      ],
      house: [
        'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=800&q=80'
      ],
      furnished: [
        'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80'
      ],
      default: [
        'https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80'
      ]
    };

    const pick = (arr: string[]) => arr[p.id % arr.length];

    if (p.sea_view) return pick(byFeature['sea']);
    if (p.is_house) return pick(byFeature['house']);
    if (p.furnished) return pick(byFeature['furnished']);
    return pick(byFeature['default']);
  }
}