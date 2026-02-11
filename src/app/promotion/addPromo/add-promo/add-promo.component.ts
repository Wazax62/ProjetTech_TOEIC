import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router'; 
import { MatDialog } from '@angular/material/dialog';
import { SuccessDialogComponent } from '../../../success-dialog/success-dialog.component';
import { NavbarComponent } from '../../../navbar/navbar.component';

@Component({
  selector: 'app-add-promo',
  standalone: true, // Add this line
  imports: [FormsModule, CommonModule, RouterModule, NavbarComponent],
  templateUrl: './add-promo.component.html',
  styleUrl: './add-promo.component.css'
})
export class AddPromoComponent {

  promoLevel = ''; // Le niveau de la promotion (ING1, ING2, ING3)
  promoSiteId = ''; // L'ID du site sélectionné

  levels: string[] = ['CP1', 'CP2', 'ING1', 'ING2', 'ING3']; // Liste des niveaux disponibles
  sites: any[] = []; // Liste des sites récupérés depuis l'API
 // Dans votre classe AddPromoComponent
  existingPromotions: any[] = []; // Initialisation explicite comme tableau vide
  errors: any = {}; // Gestion des erreurs de validation

  constructor(private router: Router, private dialog: MatDialog) {}

  ngOnInit() {
    // Load Font Awesome dynamically if not already loaded
    if (!document.querySelector('link[href*="font-awesome"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
      document.head.appendChild(link);
    }
    
    this.fetchSites(); // Récupérer les sites au chargement du composant
    this.fetchExistingPromotions(); // Récupérer les promotions existantes
  }

  // Récupération des sites depuis l'API
  fetchSites() {
    fetch('http://localhost:5000/api/sites')
      .then((res) => res.json())
      .then((data) => {
        this.sites = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des sites:', error));
  }

  // Récupération des promotions existantes
  fetchExistingPromotions() {
    fetch('http://localhost:5000/api/promotions')
      .then((res) => res.json())
      .then((data) => {
        this.existingPromotions = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des promotions existantes:', error));
  }

  // Vérifier si tous les champs obligatoires sont remplis
  isFormFilled(): boolean {
    return this.promoLevel !== '' && this.promoSiteId !== '';
  }

  // Validation du formulaire
validateForm(): boolean {
  this.errors = {};

  if (!this.promoLevel) {
    this.errors['promoLevel'] = 'Le niveau de la promotion est requis.';
  }
  if (!this.promoSiteId) {
    this.errors['promoSiteId'] = 'Le site est requis.';
  }

  // Vérification si la promotion existe déjà pour ce site
  // Assurez-vous que existingPromotions est bien un tableau avant d'utiliser some()
  if (Array.isArray(this.existingPromotions)) {
    const promotionExists = this.existingPromotions.some(
      promo => promo.nom === this.promoLevel && promo.site_id == this.promoSiteId
    );

    if (promotionExists) {
      this.errors['promoLevel'] = `La promotion ${this.promoLevel} existe déjà pour ce site. Veuillez choisir un autre niveau ou un autre site.`;
    }
  }

  return Object.keys(this.errors).length === 0;
}

  // Ajouter une promotion
  addPromo() {
    if (!this.validateForm()) {
      return;
    }

    const promo = {
      nom: this.promoLevel, // Le nom de la promotion est le niveau (ING1, ING2, ING3)
      site_id: this.promoSiteId
    };

    console.log('Envoi des données :', promo);
    fetch('http://localhost:5000/api/promotions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(promo)
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Promotion ajoutée avec succès:', data);
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'Promotion ajoutée avec succès !' },
        });

        this.dialog.afterAllClosed.subscribe(() => {
          this.router.navigate(['/promotionlist']);
        });
      })
      .catch((error) => {
        console.error('Erreur lors de l\'ajout de la promotion:', error);
      });
  }
}