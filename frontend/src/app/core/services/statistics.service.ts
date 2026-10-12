import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Statistics } from '../models/statistics.model';

@Injectable({ providedIn: 'root' })
export class StatisticsService {
  constructor(private api: ApiService) {}

  get(): Observable<Statistics> {
    return this.api.get<Statistics>('/api/statistics');
  }
}