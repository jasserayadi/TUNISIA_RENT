import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { PredictRequest, PredictResponse } from '../../core/models/prediction.model';

@Component({
  selector: 'app-result',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.scss']
})
export class ResultComponent implements OnInit {
  prediction?: PredictResponse;
  request?: PredictRequest;
  difference: number | null = null;
  differencePercent: number | null = null;

  constructor(private router: Router) {}

  ngOnInit(): void {
    const state = history.state as {
      prediction?: PredictResponse;
      request?: PredictRequest;
    };

    if (!state?.prediction) {
      this.router.navigate(['/']);
      return;
    }

    this.prediction = state.prediction;
    this.request = state.request;

    if (this.request?.advertised_price && this.prediction.estimated_rent) {
      this.difference = this.request.advertised_price - this.prediction.estimated_rent;
      this.differencePercent = Math.round(
        (this.difference / this.prediction.estimated_rent) * 100
      );
    }
  }

  get rangePosition(): number {
    if (!this.request?.advertised_price || !this.prediction) return 50;
    const { min_rent, max_rent } = this.prediction;
    const price = this.request.advertised_price;
    const clamped = Math.min(Math.max(price, min_rent), max_rent);
    return ((clamped - min_rent) / (max_rent - min_rent)) * 100;
  }

  get statusColor(): string {
    if (!this.prediction?.message) return 'secondary';
    if (this.prediction.message.startsWith('⚠')) return 'danger';
    return 'success';
  }
}