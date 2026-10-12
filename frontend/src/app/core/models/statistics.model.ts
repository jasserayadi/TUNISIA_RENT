export interface CityStat {
  city: string;
  properties: number;
  average_rent: number;
  average_surface: number;
  average_price_per_m2: number;
}

export interface Statistics {
  total_properties: number;
  average_rent: number;
  median_rent: number;
  min_rent: number;
  max_rent: number;
  average_surface: number;
  average_price_per_m2: number;
  most_represented_city?: string | null;
  furnished_average_rent: number;
  unfurnished_average_rent: number;
  by_city: CityStat[];
}