import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';  // Importer RouterModule
import { LoginComponent } from './login/login.component';  // Import LoginContainer
import { RegisterComponent } from './register/register.component';
import { ActivateAccountComponent } from './activate-account/activate-account.component';  // Import RegisterContainer
import { CommonModule } from '@angular/common'; // Pour ngClass

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,  // Permet de travailler sans module
  imports: [RouterModule, LoginComponent, RegisterComponent, CommonModule,ActivateAccountComponent]  // Ajoute les composants ici
})
export class AppComponent {
  title = 'TOEIC_APP';
}
