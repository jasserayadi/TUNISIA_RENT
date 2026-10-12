export interface Property {
  id: number;
  governorate: string;
  city: string;
  surface: number;
  bedrooms: number;
  bathrooms: number;
  floor?: number | null;
  condition?: string | null;
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
  rent: number;
  price_per_m2?: number | null;
  created_at: string;
}

export interface PropertyCreate extends Omit<Property, 'id' | 'price_per_m2' | 'created_at'> {}