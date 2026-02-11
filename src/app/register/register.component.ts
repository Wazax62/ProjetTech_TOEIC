import { Component } from '@angular/core';
import { Router, RouterModule} from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register', // Définition de l'élément HTML personnalisé pour ce composant
  templateUrl: './register.component.html', // Spécifie le fichier HTML associé à ce composant
  styleUrls: ['./register.component.css'], // Spécifie le fichier CSS associé à ce composant
  standalone: true, // Permet à ce composant d'être autonome sans module Angular supplémentaire
  imports: [FormsModule, CommonModule, RouterModule], // Importe les modules nécessaires pour les formulaires, les fonctionnalités de base et le routage
})
export class RegisterComponent {

  // Variables liées à l'affichage et à l'état des champs du formulaire
  passwordFieldType: string = 'password'; 
  passwordFieldTypeConfirmation: string = 'password'; 
  firstName: string = ''; 
  lastName: string = ''; 
  email: string = ''; 
  password: string = ''; 
  confirmPassword: string = ''; 
  errorMessage: string = ''; 
  formValid: boolean = false; 
  statusMessage: string = ''; 
  messageType: string = '';
  formTouched: boolean = false; 
  submitted: boolean = false; 

  errors: any = { // Objet pour gérer les erreurs spécifiques à chaque champ
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  };

  constructor(private router: Router) {}  // Injection du service Router pour la navigation

  // Fonction pour basculer la visibilité du mot de passe (pour les champs "Mot de passe" et "Confirmer mot de passe")
  togglePasswordVisibility(isConfirmation: boolean) {
    if (isConfirmation) {
      this.passwordFieldTypeConfirmation = this.passwordFieldTypeConfirmation === 'password' ? 'text' : 'password';
    } else {
      this.passwordFieldType = this.passwordFieldType === 'password' ? 'text' : 'password';
    }
  }

  // Fonction pour naviguer vers la page de connexion
  navigateToLogin() {
    this.router.navigate(['/login']);  
  }

  // Fonctions de validation pour chaque champ du formulaire (Prénom, Nom, Email, Mot de passe, etc.)
  validateFirstName() {
    this.errors.firstName = this.firstName.trim() ? '' : 'First name is required.'; // Validation pour le prénom
    this.updateFormValid(); // Met à jour l'état de validité du formulaire
  }

  validateLastName() {
    this.errors.lastName = this.lastName.trim() ? '' : 'Last name is required.'; // Validation pour le nom
    this.updateFormValid(); // Met à jour l'état de validité du formulaire
  }

  validateEmail() {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/; // Expression régulière pour valider l'email
    this.errors.email = this.email.trim() ? 
      (emailRegex.test(this.email) ? '' : 'Please enter a valid email address.') : 
      'Email is required.'; // Validation pour l'email
    this.updateFormValid(); // Met à jour l'état de validité du formulaire
  }

  validatePassword() {
    if (!this.password.trim()) {
      this.errors.password = 'Password is required.'; // Validation pour le mot de passe
    } else {
      const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/; // Expression régulière pour un mot de passe fort (min. 8 caractères, une lettre et un chiffre)
      this.errors.password = passwordRegex.test(this.password)
        ? ''
        : 'Password must contain at least 8 characters, one letter and one number.'; // Validation pour le mot de passe
    }
    this.updateFormValid(); // Met à jour l'état de validité du formulaire
  }

  validateConfirmPassword() {
    if (!this.confirmPassword.trim()) {
      this.errors.confirmPassword = 'Password confirmation is required.'; // Validation pour la confirmation du mot de passe
    } else {
      this.errors.confirmPassword =
        this.password === this.confirmPassword
          ? ''
          : 'Passwords do not match.'; // Validation pour s'assurer que les mots de passe correspondent
    }
    this.updateFormValid(); // Met à jour l'état de validité du formulaire
  }

  // Fonction pour valider tous les champs en une seule fois
  validateAll() {
    this.submitted = true; // Marque le formulaire comme soumis
    this.formTouched = true; // Indique que le formulaire a été touché
    this.validateFirstName(); // Valide le prénom
    this.validateLastName(); // Valide le nom
    this.validateEmail(); // Valide l'email
    this.validatePassword(); // Valide le mot de passe
    this.validateConfirmPassword(); // Valide la confirmation du mot de passe
  }

  // Met à jour l'état de validité du formulaire en fonction des erreurs
  updateFormValid() {
    this.formValid = (
      this.firstName.trim() !== '' &&
      this.lastName.trim() !== '' &&
      this.email.trim() !== '' &&
      this.password.trim() !== '' &&
      this.confirmPassword.trim() !== ''
    ) && Object.values(this.errors).every((error) => !error); // Si tous les champs sont valides et qu'il n'y a pas d'erreurs
  }

  // Fonction pour envoyer les données de l'utilisateur et procéder à l'enregistrement
  register() {
    this.validateAll(); // Valide tous les champs

    if (!this.formValid) {
      this.errorMessage = 'Please correct the errors before continuing.'; // Si le formulaire n'est pas valide, affiche un message d'erreur
      return;
    }

    this.errorMessage = ''; // Réinitialise le message d'erreur si le formulaire est valide

    const user = { // Crée un objet utilisateur avec les données du formulaire
      firstName: this.firstName,
      lastName: this.lastName,
      email: this.email,
      password: this.password,
    };

    // Envoie une requête POST pour enregistrer l'utilisateur
    fetch('http://127.0.0.1:5000/api/register', {
      method: 'POST', // Méthode HTTP POST
      headers: {
        'Content-Type': 'application/json', // Type de contenu JSON
      },
      body: JSON.stringify(user), // Envoi des données utilisateur sous forme de JSON
    })
      .then((response) => {
        return response.json().then(data => {
          return { data, status: response.status }; // Récupère la réponse JSON et le code de statut
        });
      })
      .then(({ data, status }) => {
        if (data.status === "success" && data.emailSent) { // Si l'enregistrement a réussi et un email a été envoyé
          this.statusMessage = 'Your account has been successfully created. Please check your email to activate it.'; // Message de succès
          this.messageType = 'success'; // Type de message (succès)
          this.resetForm(); // Réinitialise le formulaire après l'enregistrement
        } else {
          // Gestion des erreurs selon le code de statut HTTP
          if (status === 400) {
            this.statusMessage = data.message || 'There was an error with your registration. Please verify your information.'; // Erreur d'enregistrement
          } else if (status === 500) {
            this.statusMessage = 'A server error occurred. Please try again later or contact support.'; // Erreur serveur
          } else {
            this.statusMessage = data.message || 'An unexpected error occurred. Please try again.'; // Autre erreur
          }
          this.messageType = 'error'; // Type de message (erreur)
        }
      })
      .catch((error) => {
        console.error('Error during registration:', error); // Log de l'erreur
        this.statusMessage = 'A network error occurred. Please check your connection and try again.'; // Message d'erreur réseau
        this.messageType = 'error'; // Type de message (erreur)
      });
  }

  // Méthode pour réinitialiser le formulaire après un enregistrement réussi
  resetForm() {
    this.firstName = '';
    this.lastName = '';
    this.email = '';
    this.password = '';
    this.confirmPassword = '';
    this.errors = {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
    };
    // this.statusMessage = '';
    // this.messageType = '';
    this.submitted = false;
    this.formTouched = false;
  }
}
