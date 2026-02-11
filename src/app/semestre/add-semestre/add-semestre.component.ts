import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router'; 
import { MatDialog } from '@angular/material/dialog';
import { NavbarComponent } from '../../navbar/navbar.component';
import { SuccessDialogComponent } from '../../success-dialog/success-dialog.component';

@Component({
  selector: 'app-add-semestre',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterModule, NavbarComponent],
  templateUrl: './add-semestre.component.html',
  styleUrls: ['./add-semestre.component.css']
})
export class AddSemestreComponent {
  semestreNom = ''; // Nom du semestre (S5, S6, etc.)
  promotionId = ''; // ID de la promotion sélectionnée
  siteId = ''; // ID du site sélectionné

  promotions: any[] = []; // Liste des promotions filtrées par site
  allPromotions: any[] = []; // Liste complète des promotions
  sites: any[] = []; // Liste des sites
  existingSemestres: any[] = []; // Liste des semestres existants

  errors: any = {}; // Gestion des erreurs

  constructor(private router: Router, private dialog: MatDialog) {}

  ngOnInit() {
    this.fetchAllPromotions();
    this.fetchSites();
    this.fetchExistingSemestres();
  }

  // Récupère le nom du site sélectionné
  getSiteNom(): string {
    if (!this.siteId || !this.sites || this.sites.length === 0) return '';
    const site = this.sites.find(s => s.id == this.siteId);
    return site ? site.nom : '';
  }

  // Récupère le nom de la promotion sélectionnée
  getPromotionNom(): string {
    if (!this.promotionId || !this.promotions || this.promotions.length === 0) return '';
    const promotion = this.promotions.find(p => p.id == this.promotionId);
    return promotion ? promotion.nom : '';
  }

  // Récupération de tous les semestres existants
  fetchExistingSemestres() {
    fetch('http://localhost:5000/api/semestres')
      .then((res) => res.json())
      .then((data) => {
        this.existingSemestres = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des semestres:', error));
  }

  // Récupération de toutes les promotions
  fetchAllPromotions() {
    fetch('http://localhost:5000/api/promotions')
      .then((res) => res.json())
      .then((data) => {
        this.allPromotions = data;
      })
      .catch((error) => console.error('Erreur:', error));
  }

  // Récupération des sites
  fetchSites() {
    fetch('http://localhost:5000/api/sites')
      .then((res) => res.json())
      .then((data) => {
        this.sites = data;
      })
      .catch((error) => console.error('Erreur:', error));
  }

  // Vérifier si tous les champs obligatoires sont remplis
  isFormFilled(): boolean {
    return this.semestreNom !== '' && this.promotionId !== '' && this.siteId !== '';
  }
// Validation du formulaire
validateForm(): boolean {
  this.errors = {};

  if (!this.semestreNom) {
    this.errors['semestreNom'] = 'Le nom du semestre est requis.';
  }
  if (!this.promotionId) {
    this.errors['promotionId'] = 'La promotion est requise.';
  }
  if (!this.siteId) {
    this.errors['siteId'] = 'Le site est requis.';
  }

  // Vérification si le semestre existe déjà pour cette promotion
  // Ajouter une vérification pour s'assurer que existingSemestres est un tableau
  if (Array.isArray(this.existingSemestres)) {
    const semestreExists = this.existingSemestres.some(
      semestre => semestre.nom.toLowerCase() === this.semestreNom.toLowerCase() && 
                semestre.promotion_id == this.promotionId
    );

    if (semestreExists) {
      // Trouver le nom de la promotion pour un message plus informatif
      const promotionName = this.allPromotions.find(p => p.id == this.promotionId)?.nom || '';
      this.errors['semestreNom'] = `Le semestre "${this.semestreNom}" existe déjà pour la promotion ${promotionName}. Veuillez choisir un autre nom.`;
    }
  }

  return Object.keys(this.errors).length === 0;
}

  // Ajouter un semestre
  addSemestre() {
    if (!this.validateForm()) {
      return;
    }

    const semestre = {
      nom: this.semestreNom,
      promotion_id: this.promotionId,
      site_id: this.siteId
    };

    fetch('http://localhost:5000/api/semestres', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(semestre)
    })
      .then((response) => response.json())
      .then((data) => {
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'Semestre ajouté avec succès !' },
        });

        this.dialog.afterAllClosed.subscribe(() => {
          this.router.navigate(['/semestre']);
        });
      })
      .catch((error) => {
        console.error('Erreur:', error);
      });
  }

  // Gestion du changement de site
  onSiteChange(event: Event): void {
    this.siteId = (event.target as HTMLSelectElement).value;
    this.promotionId = ''; // Réinitialiser la promotion sélectionnée
    
    if (this.siteId) {
      // Filtrer les promotions par site
      this.promotions = this.allPromotions.filter(promo => promo.site_id == this.siteId);
    } else {
      this.promotions = [];
    }
  }
}