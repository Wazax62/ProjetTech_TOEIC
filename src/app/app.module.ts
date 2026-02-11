import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';  
import { AppComponent } from './app.component'; // ✅ Import du composant standalone
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';

import { routes } from './app.routes';

@NgModule({
  imports: [
    BrowserModule,
    RouterModule.forRoot(routes), // ✅ Utiliser forRoot pour configurer les routes principales
    AppComponent  // ✅ Importer AppComponent ici car il est standalone
  ],
  providers: [],
 
})
export class AppModule { }
