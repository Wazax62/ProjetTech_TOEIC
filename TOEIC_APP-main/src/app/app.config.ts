import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes'; // Pour les routes côté client

import { provideClientHydration, withEventReplay } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }), // Détection de changements
    provideRouter(routes), // Fournir les routes
    provideClientHydration(withEventReplay()), // Hydratation côté client
  ],
};
