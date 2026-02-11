import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router'; 
import { MatDialog } from '@angular/material/dialog';
import { NavbarComponent } from '../../navbar/navbar.component';
import { SuccessDialogComponent } from '../../success-dialog/success-dialog.component';

@Component({
  selector: 'app-update-semestre',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterModule, NavbarComponent],
  templateUrl: './update-semestre.component.html',
  styleUrls: ['./update-semestre.component.css']
})
export class UpdateSemestreComponent implements OnInit {
  semestreNom = ''; // Nom du semestre (S5, S6, etc.)
  promotionId = ''; // ID de la promotion sélectionnée
  siteId = ''; // ID du site sélectionné
  semestreId = ''; // ID du semestre à modifier

  promotions: any[] = []; // Liste des promotions filtrées par site
  allPromotions: any[] = []; // Liste complète des promotions
  sites: any[] = []; // Liste des sites

  errors: any = {}; // Gestion des erreurs

  constructor(
    private router: Router, 
    private dialog: MatDialog,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.semestreId = this.route.snapshot.paramMap.get('id') || '';
    this.fetchSemestreData();
    this.fetchAllPromotions();
    this.fetchSites();
  }

  // Récupérer les données du semestre existant
  fetchSemestreData() {
    fetch(`http://localhost:5000/api/semestres/${this.semestreId}`)
      .then((res) => res.json())
      .then((data) => {
        this.semestreNom = data.nom;
        this.promotionId = data.promotion_id;
        this.siteId = data.site_id;

        console.log('voila le semestre : ',data)
        // Filtrer les promotions pour le site sélectionné
        this.onSiteChange({ target: { value: this.siteId } } as any);
      })
      .catch((error) => console.error('Erreur:', error));
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

    return Object.keys(this.errors).length === 0;
  }

  // Mettre à jour un semestre
  updateSemestre() {
    if (!this.validateForm()) {
      return;
    }

    const semestre = {
      nom: this.semestreNom,
      promotion_id: this.promotionId,
      site_id: this.siteId
    };

    fetch(`http://localhost:5000/api/semestres/${this.semestreId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(semestre)
    })
      .then((response) => response.json())
      .then((data) => {
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'Semestre mis à jour avec succès !' },
        });

        this.dialog.afterAllClosed.subscribe(() => {
          this.router.navigate(['/semestre']);
        });
      })
      .catch((error) => {
        console.error('Erreur:', error);
        this.errors['general'] = 'Une erreur est survenue lors de la mise à jour';
      });
  }

  // Gestion du changement de site
  onSiteChange(event: Event | any): void {
    // Gestion à la fois pour l'événement et pour l'initialisation
    const siteId = event.target?.value || event;
    this.siteId = siteId;
    this.promotionId = ''; // Réinitialiser la promotion sélectionnée
    
    if (this.siteId) {
      // Filtrer les promotions par site
      this.promotions = this.allPromotions.filter(promo => promo.site_id == this.siteId);
    } else {
      this.promotions = [];
    }
  }
}