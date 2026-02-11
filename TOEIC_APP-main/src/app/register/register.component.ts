import { Component } from '@angular/core';
import { Router} from '@angular/router'; // Pour la redirection
import { FormsModule } from '@angular/forms'; // Pour ngModel
import { CommonModule } from '@angular/common';




@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css'],
  imports: [FormsModule,CommonModule], 

})
export class RegisterComponent {

  passwordFieldType: string = 'password';

 

  togglePasswordVisibility() {
    this.passwordFieldType = this.passwordFieldType === 'password' ? 'text' : 'password';
  }

  navigateToLogin() {
    this.router.navigate(['/login']);  // Fonction pour naviguer vers la page d'inscription
  }



  firstName: string = '';
  lastName: string = '';
  email: string = '';
  password: string = '';
  confirmPassword: string = '';
  errorMessage: string = ''; 
  formValid: boolean = false; 
  statusMessage: string = ''; 
  messageType: string = ''; 

  errors: any = {
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  };

  constructor(private router: Router) {}  



  validateFirstName() {
    this.errors.firstName = this.firstName.trim() ? '' : 'Le prénom est requis.';
    console.log('First Name Error:', this.errors.firstName); 
    this.updateFormValid();
  }
  
  validateLastName() {
    this.errors.lastName = this.lastName.trim() ? '' : 'Le nom est requis.';
    console.log('Last Name Error:', this.errors.lastName);  
    this.updateFormValid();
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

  validateConfirmPassword() {
    this.errors.confirmPassword =
      this.password === this.confirmPassword
        ? ''
        : 'Les mots de passe ne correspondent pas.';
    this.updateFormValid();
  }

  updateFormValid() {
   
    this.formValid = (
      this.firstName.trim() !== '' &&
      this.lastName.trim() !== '' &&
      this.email.trim() !== '' &&
      this.password.trim() !== '' &&
      this.confirmPassword.trim() !== ''
    ) && Object.values(this.errors).every((error) => !error);
  }

  register() {
    if (!this.formValid) {
      this.errorMessage = 'Veuillez corriger les erreurs avant de continuer.';
      return;
    }


  const user = {
      firstName: this.firstName,
      lastName: this.lastName,
      email: this.email,
      password: this.password,
    };

   
  fetch('http://127.0.0.1:5000/api/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(user),
  })
    .then((response) => {
      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      return response.json();
    })
    .then((data) => {
      if (data.status === "success" && data.emailSent) {
        this.statusMessage = 'Votre compte est créé avec succès. Veuillez vérifier votre boîte email pour l’activer.';
        this.messageType = 'success';
      } else if (data.status === "success" && !data.emailSent) {
        this.statusMessage = 'Votre compte est créé, mais une erreur est survenue lors de l’envoi de l’email. Veuillez contacter le support.';
        this.messageType = 'error';
      } else {
        this.statusMessage = 'Une erreur est survenue lors de la création du compte. Veuillez réessayer.';
        this.messageType = 'error';
      }
    })
   
    .catch((error) => {
      console.error('Erreur lors de l\'enregistrement:', error);
      this.statusMessage = 'Une erreur est survenue. Veuillez réessayer.';
      this.messageType = 'error';
    });
}


}