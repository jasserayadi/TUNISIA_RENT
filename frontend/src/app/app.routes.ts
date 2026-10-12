import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/home/home.component').then((m) => m.HomeComponent),
    title: 'TounesRent — Estimator'
  },
  {
    path: 'recommend',
    loadComponent: () =>
      import('./features/recommend/recommend.component').then((m) => m.RecommendComponent),
    title: 'TounesRent — AI Recommendations'
  },
  {
    path: 'result',
    loadComponent: () =>
      import('./features/result/result.component').then((m) => m.ResultComponent),
    title: 'TounesRent — Result'
  },
  {
    path: 'properties',
    loadComponent: () =>
      import('./features/properties/properties-list.component')
        .then((m) => m.PropertiesListComponent),
    title: 'TounesRent — Properties'
  },
  {
    path: 'add-property',
    loadComponent: () =>
      import('./features/add-property/add-property.component')
        .then((m) => m.AddPropertyComponent),
    title: 'TounesRent — Add Property'
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component')
        .then((m) => m.DashboardComponent),
    title: 'TounesRent — Dashboard'
  },
  { path: '**', redirectTo: '' }
];