import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { routes } from './app.routes';  // Importer les routes définies

@NgModule({
  imports: [RouterModule.forRoot(routes)],  // Utiliser les routes ici
  exports: [RouterModule]  // Exporter le RouterModule pour qu'il soit utilisé partout
})
export class AppRoutingModule { }
