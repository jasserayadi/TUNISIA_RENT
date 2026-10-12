import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './shared/navbar/navbar.component';
import { ToastHostComponent } from './shared/toast-host/toast-host.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, ToastHostComponent],
  template: `
    <app-navbar></app-navbar>
    <main class="tr-main">
      <router-outlet></router-outlet>
    </main>
    <footer class="tr-footer">
      <div class="container text-center small text-muted py-3">
        TounesRent 🇹🇳 — Estimations are indicative and not official valuations.
      </div>
    </footer>
    <app-toast-host></app-toast-host>
  `,
  styles: [`
    :host { display: flex; flex-direction: column; min-height: 100vh; }
    .tr-main { flex: 1; }
    .tr-footer {
      background: var(--tr-surface);
      border-top: 1px solid var(--tr-border);
      margin-top: 40px;
    }
  `]
})
export class AppComponent {}