import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-activate-account',
  templateUrl: './activate-account.component.html',
  styleUrls: ['./activate-account.component.css'],
  imports: [FormsModule, CommonModule],
})
export class ActivateAccountComponent implements OnInit {
  
  // Déclaration des variables
  statusMessage: string = ''; 
  messageType: string = ''; 
  loading: boolean = true; 
  token: string = ''; 

  // Constructeur pour injecter les dépendances
  constructor(private route: ActivatedRoute, private router: Router) {}

  // Méthode ngOnInit appelée lors de l'initialisation du composant
  ngOnInit(): void {
    // Simule un délai de chargement pour afficher une animation
    setTimeout(() => {
      this.token = this.route.snapshot.paramMap.get('token') || ''; // Récupère le token depuis l'URL
      if (this.token) {
        // Si un token est trouvé, tenter l'activation
        this.activateAccount(this.token);
      } else {
        // Si aucun token n'est trouvé, afficher un message d'erreur
        this.loading = false;
        this.statusMessage = 'Aucun token d\'activation trouvé.';
        this.messageType = 'error';
      }
    }, 1500); // Délai de 1.5 seconde pour l'animation de chargement
  }

  // Méthode pour activer le compte avec le token
  activateAccount(token: string) {
    // Envoie une requête à l'API pour activer le compte
    fetch(`http://127.0.0.1:5000/api/activate/${token}`)
      .then((response) => response.json()) // Conversion de la réponse en JSON
      .then((data) => {
        // Une fois la réponse reçue
        this.loading = false; // Désactive l'animation de chargement
        if (data.status === 'success') {
          // Si l'activation a réussi
          this.statusMessage = 'Votre compte a été activé avec succès. Vous pouvez maintenant vous connecter et accéder à toutes les fonctionnalités de notre plateforme.';
          this.messageType = 'success'; // Type du message est 'success'
        } else {
          // Si l'activation a échoué
          this.statusMessage = data.message || 'Le lien d\'activation est invalide ou a expiré. Veuillez contacter le support si vous avez besoin d\'aide.';
          this.messageType = 'error'; // Type du message est 'error'
        }
      })
      .catch((error) => {
        // En cas d'erreur lors de la requête
        this.loading = false; // Désactive l'animation de chargement
        this.statusMessage = 'Une erreur est survenue lors de l\'activation du compte. Veuillez réessayer ultérieurement ou contacter le support.';
        this.messageType = 'error'; // Type du message est 'error'
        console.error('Erreur d\'activation:', error); // Affiche l'erreur dans la console
      });
  }

  // Méthode pour naviguer vers la page de connexion
  navigateToLogin() {
    this.router.navigate(['/login']); // Redirige l'utilisateur vers la page de login
  }

  // Méthode pour réessayer l'activation
  tryAgain() {
    this.loading = true; // Active l'animation de chargement
    setTimeout(() => {
      // Essaye de réactiver le compte avec le même token
      if (this.token) {
        this.activateAccount(this.token);
      } else {
        // Si aucun token n'est trouvé, afficher un message d'erreur
        this.loading = false;
        this.statusMessage = 'Aucun token d\'activation trouvé.';
      }
    }, 1000); // Délai de 1 seconde avant la réactivation
  }

  // Méthode pour naviguer vers la page d'accueil
  navigateToHome() {
    this.router.navigate(['/']); // Redirige l'utilisateur vers la page d'accueil
  }
}
