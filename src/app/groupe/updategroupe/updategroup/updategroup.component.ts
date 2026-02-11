import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';
import { SuccessDialogComponent } from '../../../success-dialog/success-dialog.component';
import { RouterModule } from '@angular/router';
import { NavbarComponent } from '../../../navbar/navbar.component';

@Component({
  selector: 'app-update-group',
  standalone: true,
  imports: [FormsModule, CommonModule,RouterModule, NavbarComponent],
  templateUrl: './updategroup.component.html',
  styleUrl: './updategroup.component.css'
})
export class UpdateGroupComponent implements OnInit {
  group: any = {
    nom: '',
    promotion_id: '',
    site_id: '',
    semestre_id: ''
  };

  groupId!: string;
  promotions: any[] = [];
  sites: any[] = [];
  semestres: any[] = [];

  filteredPromotions: any[] = []; // Promotions filtrées par site
  filteredSemestres: any[] = []; // Semestres filtrés par site et promotion

  errors: { [key: string]: string } = {};

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private dialog: MatDialog
  ) { }

  ngOnInit() {
    this.groupId = this.route.snapshot.paramMap.get('id')!;
    this.getGroupDetails();
    this.fetchSites();
  }

  // Récupérer les détails du groupe
  getGroupDetails() {
    fetch(`http://localhost:5000/api/groupes/${this.groupId}`)
      .then((response) => response.json())
      .then((data) => {
        console.log('Group details:', data);
        this.group = data;
        console.log("voila le grp apres asse:",this.group)

        if (this.group.site_id) {
          this.fetchPromotionsBySite(this.group.site_id);
        }
        if (this.group.promotion_id) {
          this.fetchSemestresBySiteAndPromotion(this.group.site_id, this.group.promotion_id);
        }
      })
      .catch((error) => console.error("Erreur lors de la récupération des détails du groupe:", error));
  }

  // Récupérer les sites
  fetchSites() {
    fetch('http://localhost:5000/api/sites')
      .then((res) => res.json())
      .then((data) => {
        this.sites = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des sites:', error));
  }

  // Récupérer les promotions filtrées par site
  fetchPromotionsBySite(siteId: string) {
    fetch(`http://localhost:5000/api/promotions/by_site/${siteId}`)
      .then((res) => res.json())
      .then((data) => {
        this.filteredPromotions = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des promotions:', error));
  }

  // Récupérer les semestres filtrés par site et promotion
  fetchSemestresBySiteAndPromotion(siteId: string, promotionId: string) {
    fetch(`http://localhost:5000/api/semestres/by_promotion?promotion_id=${promotionId}`)
      .then((res) => res.json())
      .then((data) => {
        this.filteredSemestres = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des semestres:', error));
  }

  // Lorsque le site est sélectionné
  onSiteChange(siteId: string) {
    this.group.site_id = siteId;
    this.group.promotion_id = ''; // Réinitialiser la promotion sélectionnée
    this.group.semestre_id = ''; // Réinitialiser le semestre sélectionné
    this.filteredPromotions = []; // Réinitialiser les promotions filtrées
    this.filteredSemestres = []; // Réinitialiser les semestres filtrés

    if (siteId) {
      this.fetchPromotionsBySite(siteId);
    }
  }

  // Lorsque la promotion est sélectionnée
  onPromotionChange(promotionId: string) {
    this.group.promotion_id = promotionId;
    this.group.semestre_id = ''; // Réinitialiser le semestre sélectionné
    this.filteredSemestres = []; // Réinitialiser les semestres filtrés

    if (promotionId && this.group.site_id) {
      this.fetchSemestresBySiteAndPromotion(this.group.site_id, promotionId);
    }
  }

  // Validation du formulaire
  validateForm(): boolean {
    this.errors = {};

    if (!this.group.nom.trim()) this.errors['groupName'] = 'Le nom du groupe est requis.';
    if (!this.group.promotion_id) this.errors['groupPromotionId'] = 'Veuillez choisir une promotion.';
    if (!this.group.site_id) this.errors['groupSiteId'] = 'Veuillez choisir un site.';
    if (!this.group.semestre_id) this.errors['groupSemestreId'] = 'Veuillez choisir un semestre.';

    return Object.keys(this.errors).length === 0;
  }

  // Modifier le groupe
  updateGroup() {
    if (!this.validateForm()) {
      return;
    }

    console.log('Data being sent:', this.group); // Log the data

    fetch(`http://localhost:5000/api/groupes/${this.groupId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(this.group)
    })
      .then((response) => response.json())
      .then((data) => {
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'Groupe mis à jour avec succès !' },
        });

        this.dialog.afterAllClosed.subscribe(() => {
          this.router.navigate(['/groupelist']);
        });
      })
      .catch((error) => console.error('Erreur lors de la mise à jour du groupe:', error));
  }
}