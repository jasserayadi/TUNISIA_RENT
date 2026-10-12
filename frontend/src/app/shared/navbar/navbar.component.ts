import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { ThemeService } from '../../core/services/theme.service';


@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  template: `
    <nav class="tr-nav">
      <div class="container tr-nav-inner">
        <a class="tr-brand" routerLink="/">
          <span class="tr-brand-icon">🏠</span>
          <span class="tr-brand-text">TounesRent <small>🇹🇳</small></span>
        </a>

        <button
          class="tr-nav-toggle"
          (click)="menuOpen = !menuOpen"
          aria-label="Toggle menu">
          <i class="bi" [ngClass]="menuOpen ? 'bi-x-lg' : 'bi-list'"></i>
        </button>

        <ul class="tr-nav-links" [class.open]="menuOpen">
          <li>
            <a routerLink="/" routerLinkActive="active"
               [routerLinkActiveOptions]="{ exact: true }" (click)="menuOpen = false">
              <i class="bi bi-calculator"></i> Estimator
            </a>
          </li>
          <li>
            <a routerLink="/recommend" routerLinkActive="active" (click)="menuOpen = false">
              <i class="bi bi-stars"></i> AI Picks
            </a>
          </li>
          <li>
            <a routerLink="/properties" routerLinkActive="active" (click)="menuOpen = false">
              <i class="bi bi-building"></i> Properties
            </a>
          </li>
          <li>
            <a routerLink="/add-property" routerLinkActive="active" (click)="menuOpen = false">
              <i class="bi bi-plus-circle"></i> Add
            </a>
          </li>
          <li>
            <a routerLink="/dashboard" routerLinkActive="active" (click)="menuOpen = false">
              <i class="bi bi-bar-chart"></i> Dashboard
            </a>
          </li>
          <li>
            <button class="tr-theme-btn" (click)="theme.toggle()" title="Toggle theme">
              <i class="bi" [ngClass]="theme.theme() === 'dark' ? 'bi-sun-fill' : 'bi-moon-stars-fill'"></i>
            </button>
          </li>
        </ul>
      </div>
    </nav>
  `,
  styles: [`
    .tr-nav {
      position: sticky;
      top: 0;
      z-index: 1030;
      backdrop-filter: saturate(180%) blur(14px);
      background: color-mix(in srgb, var(--tr-surface) 80%, transparent);
      border-bottom: 1px solid var(--tr-border);
    }
    .tr-nav-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      gap: 16px;
    }
    .tr-brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 800;
      font-size: 1.15rem;
      color: var(--tr-text);
      letter-spacing: -0.02em;
    }
    .tr-brand-icon {
      font-size: 1.5rem;
      filter: drop-shadow(0 4px 8px rgba(13,110,253,.35));
    }
    .tr-brand-text small { opacity: .7; }

    .tr-nav-links {
      list-style: none;
      margin: 0;
      padding: 0;
      display: flex;
      gap: 6px;
      align-items: center;
    }
    .tr-nav-links a,
    .tr-theme-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 14px;
      border-radius: 999px;
      color: var(--tr-text-muted);
      font-weight: 600;
      font-size: .92rem;
      border: 1px solid transparent;
      background: transparent;
      cursor: pointer;
      transition: all var(--tr-transition);
    }
    .tr-nav-links a:hover,
    .tr-theme-btn:hover {
      color: var(--tr-primary);
      background: color-mix(in srgb, var(--tr-primary) 10%, transparent);
    }
    .tr-nav-links a.active {
      color: #fff;
      background: linear-gradient(135deg, var(--tr-primary), var(--tr-primary-dark));
      box-shadow: 0 6px 14px rgba(13,110,253,.35);
    }
    .tr-theme-btn {
      width: 40px;
      height: 40px;
      padding: 0;
      justify-content: center;
      border: 1px solid var(--tr-border);
    }

    .tr-nav-toggle {
      display: none;
      background: transparent;
      border: 0;
      color: var(--tr-text);
      font-size: 1.4rem;
      cursor: pointer;
    }

    @media (max-width: 860px) {
      .tr-nav-toggle { display: block; }
      .tr-nav-links {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        flex-direction: column;
        align-items: stretch;
        gap: 4px;
        padding: 12px 16px 20px;
        background: var(--tr-surface);
        border-bottom: 1px solid var(--tr-border);
        transform: translateY(-10px);
        opacity: 0;
        pointer-events: none;
        transition: all var(--tr-transition);
      }
      .tr-nav-links.open {
        transform: translateY(0);
        opacity: 1;
        pointer-events: auto;
      }
      .tr-nav-links a { justify-content: flex-start; }
      .tr-theme-btn { align-self: flex-start; }
    }
  `]
})
export class NavbarComponent {
  protected readonly theme = inject(ThemeService);
  menuOpen = false;
}