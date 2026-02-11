import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';  // Assure-toi que RouterModule est importé
import { AppComponent } from './app.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';

import { routes } from './app.routes'; // Importer tes routes ici

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    RegisterComponent
  ],
  imports: [
    BrowserModule,
    RouterModule.forRoot(routes), // Utiliser forRoot pour configurer les routes principales
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
