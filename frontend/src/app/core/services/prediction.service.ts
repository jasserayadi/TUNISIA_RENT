import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { PredictRequest, PredictResponse } from '../models/prediction.model';

@Injectable({ providedIn: 'root' })
export class PredictionService {
  constructor(private api: ApiService) {}

  predict(payload: PredictRequest): Observable<PredictResponse> {
    return this.api.post<PredictResponse>('/api/predict', payload);
  }
}