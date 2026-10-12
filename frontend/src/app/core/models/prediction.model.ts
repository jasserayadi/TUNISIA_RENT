import { Property } from './property.model';

export interface PredictRequest {
  governorate: string;
  city: string;
  surface: number;
  bedrooms: number;
  bathrooms: number;
  is_house: boolean;
  furnished: boolean;
  parking: boolean;
  elevator: boolean;
  aircon: boolean;
  heating: boolean;
  security: boolean;
  pool: boolean;
  sea_view: boolean;
  terrace: boolean;
  equipped_kitchen: boolean;
  advertised_price?: number | null;
}

export interface PredictResponse {
  estimated_rent: number;
  min_rent: number;
  max_rent: number;
  currency: string;
  price_per_m2?: number | null;
  confidence?: string | null;
  message?: string | null;
  similar_properties: Property[];
}