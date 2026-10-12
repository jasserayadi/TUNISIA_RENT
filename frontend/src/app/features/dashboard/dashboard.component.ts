import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Statistics } from '../../core/models/statistics.model';
import { StatisticsService } from '../../core/services/statistics.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  stats?: Statistics;
  loading = false;
  error: string | null = null;

  constructor(private statisticsService: StatisticsService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.statisticsService.get().subscribe({
      next: (data) => {
        this.stats = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'Could not load statistics.';
        this.loading = false;
      }
    });
  }

  get maxCityProperties(): number {
    if (!this.stats?.by_city.length) return 1;
    return Math.max(...this.stats.by_city.map((c) => c.properties));
  }

  barWidth(count: number): number {
    return (count / this.maxCityProperties) * 100;
  }
}