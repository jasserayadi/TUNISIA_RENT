import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Property, PropertyCreate } from '../models/property.model';

@Injectable({ providedIn: 'root' })
export class PropertyService {
  constructor(private api: ApiService) {}

  list(filters: Record<string, any> = {}): Observable<Property[]> {
    return this.api.get<Property[]>('/api/properties', filters);
  }

  get(id: number): Observable<Property> {
    return this.api.get<Property>(`/api/properties/${id}`);
  }

  create(payload: PropertyCreate): Observable<Property> {
    return this.api.post<Property>('/api/properties', payload);
  }

  update(id: number, payload: Partial<Property>): Observable<Property> {
    return this.api.put<Property>(`/api/properties/${id}`, payload);
  }

  delete(id: number): Observable<void> {
    return this.api.delete<void>(`/api/properties/${id}`);
  }

  similar(params: {
    governorate?: string;
    city?: string;
    surface?: number;
    bedrooms?: number;
    limit?: number;
  }): Observable<Property[]> {
    return this.api.get<Property[]>('/api/properties/similar', params);
  }
}