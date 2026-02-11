import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';  // Ajout de l'import pour Router

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [FormsModule, CommonModule]
})
export class LoginComponent {
  passwordFieldType: string = 'password';

  email: string = '';
  password: string = '';
  errorMessage: string = ''; 
  successMessage: string = '';
  formValid: boolean = false;

  errors: any = {
    email: '',
    password: '',
  };

  statusMessage: string = '';
  messageType: string = '';

  constructor(private router: Router) {}

  togglePasswordVisibility() {
    this.passwordFieldType = this.passwordFieldType === 'password' ? 'text' : 'password';
  }

  navigateToRegister() {
    this.router.navigate(['/register']); 
  }

  validateEmail() {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@etu\.eilco\.univ-littoral\.fr$/;
    this.errors.email = emailRegex.test(this.email)
      ? ''
      : 'Veuillez entrer un email académique valide.';
    this.updateFormValid();
  }

  validatePassword() {
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/; // Minimum 8 caractères, 1 lettre et 1 chiffre
    this.errors.password = passwordRegex.test(this.password)
      ? ''
      : 'Le mot de passe doit contenir au moins 8 caractères, une lettre et un chiffre.';
    this.updateFormValid();
  }

  updateFormValid() {
    this.formValid = (
      this.email.trim() !== '' &&
      this.password.trim() !== '' &&
      Object.values(this.errors).every((error) => !error)
    );
  }

  login() {
    if (!this.formValid) {
      this.errorMessage = 'Veuillez corriger les erreurs avant de continuer.';
      this.statusMessage = this.errorMessage;
      this.messageType = 'error';
      return;
    }

    const userCredentials = {
      email: this.email,
      password: this.password,
    };

    fetch('http://127.0.0.1:5000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userCredentials),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Erreur HTTP : ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (data.status === 'success' && data.accountActivated) {
          this.successMessage = 'Connexion réussie. Bienvenue !';
          this.statusMessage = this.successMessage;
          this.messageType = 'success';
          this.router.navigate(['/dashboard']);  // Redirection vers le dashboard après connexion réussie
        } else if (data.status === 'success' && !data.accountActivated) {
          this.errorMessage = 'Votre compte n\'est pas encore activé. Veuillez vérifier votre email.';
          this.statusMessage = this.errorMessage;
          this.messageType = 'error';
        } else {
          this.errorMessage = 'Nom d\'utilisateur ou mot de passe incorrect.';
          this.statusMessage = this.errorMessage;
          this.messageType = 'error';
        }
      })
      .catch((error) => {
        console.error('Erreur lors de la connexion:', error);
        this.errorMessage = 'Une erreur est survenue. Veuillez réessayer.';
        this.statusMessage = this.errorMessage;
        this.messageType = 'error';
      });
  }
}
