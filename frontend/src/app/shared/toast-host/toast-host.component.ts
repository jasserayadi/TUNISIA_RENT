import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ToastService } from '../../core/services/toast.service';

@Component({
  selector: 'app-toast-host',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="tr-toast-stack">
      <div *ngFor="let t of toastService.toasts()" class="tr-toast" [ngClass]="t.type">
        <div class="d-flex align-items-start gap-2">
          <i class="bi"
             [ngClass]="{
               'bi-check-circle-fill text-success': t.type === 'success',
               'bi-exclamation-triangle-fill text-danger': t.type === 'error',
               'bi-info-circle-fill text-primary': t.type === 'info'
             }"></i>
          <div class="flex-grow-1">{{ t.message }}</div>
          <button class="close" (click)="toastService.dismiss(t.id)" aria-label="Close">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .tr-toast-stack {
      position: fixed;
      right: 20px;
      bottom: 20px;
      z-index: 1080;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
  `]
})
export class ToastHostComponent {
  protected readonly toastService = inject(ToastService);
}