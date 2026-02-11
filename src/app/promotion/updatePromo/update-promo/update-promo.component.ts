
import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';
import { SuccessDialogComponent } from '../../../success-dialog/success-dialog.component';
import { NavbarComponent } from '../../../navbar/navbar.component';

@Component({
  selector: 'app-update-promo',
  imports: [FormsModule, CommonModule,RouterModule,NavbarComponent],
  templateUrl: './update-promo.component.html',
  styleUrl: './update-promo.component.css'
})
export class UpdatePromoComponent implements OnInit {
  promoId: number; // ID de la promotion à mettre à jour
  promoLevel = ''; // Niveau de la promotion (ING1, ING2, ING3)
  promoSiteId = ''; // ID du site sélectionné

  levels: string[] = ['ING1', 'ING2', 'ING3']; // Liste des niveaux disponibles
  sites: any[] = []; // Liste des sites récupérés depuis l'API

  errors: any = {}; // Gestion des erreurs de validation

  constructor(private router: Router, private route: ActivatedRoute, private dialog: MatDialog) {
    this.promoId = this.route.snapshot.params['id']; // Récupérer l'ID de la promotion depuis l'URL
  }

  ngOnInit() {
    this.fetchPromo(); // Récupérer les détails de la promotion
    this.fetchSites(); // Récupérer les sites
  }

  // Récupérer les détails de la promotion à mettre à jour
  fetchPromo() {
    fetch(`http://localhost:5000/api/promotions/${this.promoId}`)
      .then((res) => res.json())
      .then((data) => {
        this.promoLevel = data.nom; // Le nom de la promotion est le niveau
        this.promoSiteId = data.site_id;
      })
      .catch((error) => console.error('Erreur lors du chargement de la promotion:', error));
  }

  // Récupérer les sites depuis l'API
  fetchSites() {
    fetch('http://localhost:5000/api/sites')
      .then((res) => res.json())
      .then((data) => {
        this.sites = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des sites:', error));
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

    return Object.keys(this.errors).length === 0;
  }

  // Mettre à jour la promotion
  updatePromo() {
    if (!this.validateForm()) {
      return;
    }

    const promo = {
      nom: this.promoLevel, // Le nom de la promotion est le niveau
      site_id: this.promoSiteId
    };

    console.log('Envoi des données :', promo);
    fetch(`http://localhost:5000/api/promotions/${this.promoId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(promo)
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Promotion mise à jour avec succès:', data);
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'Promotion mise à jour avec succès !' },
        });

        this.dialog.afterAllClosed.subscribe(() => {
          this.router.navigate(['/promolist']);
        });
      })
      .catch((error) => {
        console.error('Erreur lors de la mise à jour de la promotion:', error);
      });
  }
}