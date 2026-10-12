import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { Property } from '../models/property.model';
import { PredictRequest, PredictResponse } from '../models/prediction.model';
import { PredictionService } from './prediction.service';
import { PropertyService } from './property.service';

export interface Recommendation {
  prediction: PredictResponse;
  matches: Property[];
}

@Injectable({ providedIn: 'root' })
export class RecommendService {
  constructor(
    private predictionService: PredictionService,
    private propertyService: PropertyService
  ) {}

  recommend(payload: PredictRequest, tolerance = 0.15, limit = 10): Observable<Recommendation> {
    return this.predictionService.predict(payload).pipe(
      switchMap((prediction: PredictResponse) => {
        const minAllowed = prediction.min_rent * (1 - tolerance);
        const maxAllowed = prediction.max_rent * (1 + tolerance);

        return this.propertyService
          .similar({
            governorate: payload.governorate,
            city: payload.city,
            surface: payload.surface,
            bedrooms: payload.bedrooms,
            limit: 50
          })
          .pipe(
            map((props) =>
              props
                .filter((p) => p.rent >= minAllowed && p.rent <= maxAllowed)
                .sort(
                  (a, b) =>
                    Math.abs(a.rent - prediction.estimated_rent) -
                    Math.abs(b.rent - prediction.estimated_rent)
                )
                .slice(0, limit)
            ),
            map((matches) => ({ prediction, matches }))
          );
      })
    );
  }

  recommendWithFallback(
    payload: PredictRequest,
    tolerance = 0.15,
    limit = 10
  ): Observable<Recommendation> {
    return this.recommend(payload, tolerance, limit).pipe(
      switchMap((rec) => {
        if (rec.matches.length > 0) return [rec];

        return this.propertyService
          .similar({
            governorate: payload.governorate,
            city: payload.city,
            surface: payload.surface,
            bedrooms: payload.bedrooms,
            limit
          })
          .pipe(map((matches) => ({ prediction: rec.prediction, matches })));
      })
    );
  }
}