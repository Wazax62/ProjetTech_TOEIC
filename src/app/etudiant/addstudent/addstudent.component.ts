import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';
import { SuccessDialogComponent } from '../../success-dialog/success-dialog.component';
import { NavbarComponent } from '../../navbar/navbar.component';

@Component({
  selector: 'app-addstudent',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink, NavbarComponent],
  templateUrl: './addstudent.component.html',
  styleUrls: ['./addstudent.component.css']
})
export class AddstudentComponent implements OnInit {
  // Propriétés pour lier les champs du formulaire
  studentLastName = '';
  studentFirstName = '';
  studentSiteId = '';
  studentPromotionId = '';
  studentSemestreId = '';
  studentGroupId = '';
  studentSpecialite = '';
  //studentEmail = '';

  // Listes pour les sélections
  sites: any[] = [];
  promotions: any[] = [];
  semestres: any[] = [];
  groupes: any[] = [];
  specialites: string[] = [
    'Informatique',
    'Génie Industriel',
    'Génie Energétique et Environnement',
    'Agroalimentaire'
  ];

  // Propriétés pour gérer les erreurs
  errors: any = {};

  constructor(private router: Router, private dialog: MatDialog) {}

  ngOnInit() {
    // Charger les listes dès que le composant est monté
    this.fetchSites();
  }

  // Récupération des sites
  fetchSites() {
    fetch('http://localhost:5000/api/sites')
      .then((res) => res.json())
      .then((data) => {
        this.sites = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des sites:', error));
  }

  // Lorsque le site est sélectionné
  onSiteChange(siteId: string) {
    this.studentSiteId = siteId;
    this.studentPromotionId = '';
    this.studentSemestreId = '';
    this.studentGroupId = '';
    this.promotions = [];
    this.semestres = [];
    this.groupes = [];

    if (siteId) {
      this.fetchPromotionsBySite(siteId);
    }
  }

  // Récupération des promotions par site
  fetchPromotionsBySite(siteId: string) {
    fetch(`http://localhost:5000/api/promotions/by_site/${siteId}`)
      .then((res) => res.json())
      .then((data) => {
        this.promotions = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des promotions:', error));
  }

  // Lorsque la promotion est sélectionnée
  onPromotionChange(promotionId: string) {
    this.studentPromotionId = promotionId;
    this.studentSemestreId = '';
    this.studentGroupId = '';
    this.semestres = [];
    this.groupes = [];

    if (promotionId) {
      this.fetchSemestresByPromotion(promotionId);
    }
  }

  // Récupération des semestres par promotion
  fetchSemestresByPromotion(promotionId: string) {
    fetch(`http://localhost:5000/api/semestres/by_promotion?promotion_id=${promotionId}`)
      .then((res) => res.json())
      .then((data) => {
        this.semestres = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des semestres:', error));
  }

  // Lorsque le semestre est sélectionné
  onSemestreChange(semestreId: string) {
    this.studentSemestreId = semestreId;
    this.studentGroupId = '';
    this.groupes = [];

    if (semestreId && this.studentPromotionId && this.studentSiteId) {
      this.fetchGroupesBySitePromotionSemestre(this.studentSiteId, this.studentPromotionId, semestreId);
    }
  }

  // Récupération des groupes par site, promotion et semestre
  fetchGroupesBySitePromotionSemestre(siteId: string, promotionId: string, semestreId: string) {
    const url = `http://localhost:5000/api/groupes/by_site_promotion_semestre?site_id=${siteId}&promotion_id=${promotionId}&semestre_id=${semestreId}`;

    fetch(url)
      .then((res) => {
        if (!res.ok) {
          throw new Error('Erreur lors du chargement des groupes');
        }
        return res.json();
      })
      .then((data) => {
        this.groupes = data;
      })
      .catch((error) => {
        console.error('Erreur lors du chargement des groupes:', error);
        this.groupes = []; // Réinitialiser la liste des groupes en cas d'erreur
      });
  }

  // Méthode pour vérifier les erreurs dans le formulaire
  validateForm(): boolean {
    this.errors = {}; // Réinitialise les erreurs

    // Vérification des champs
    if (!this.studentLastName) this.errors['studentLastName'] = 'Le nom est requis.';
    if (!this.studentFirstName) this.errors['studentFirstName'] = 'Le prénom est requis.';
    if (!this.studentSiteId) this.errors['studentSiteId'] = 'Le site est requis.';
    if (!this.studentPromotionId) this.errors['studentPromotionId'] = 'La promotion est requise.';
    if (!this.studentSemestreId) this.errors['studentSemestreId'] = 'Le semestre est requis.';
    if (!this.studentGroupId) this.errors['studentGroupId'] = 'Le groupe est requis.';
    if (!this.studentSpecialite) this.errors['studentSpecialite'] = 'La spécialité est requise.';
    //if (!this.studentEmail) this.errors['studentEmail'] = 'L\'email est requis.';

    // Si des erreurs existent, ne pas soumettre le formulaire
    return Object.keys(this.errors).length === 0;
  }

  // Méthode pour envoyer les données du formulaire avec fetch
  addStudent() {
    // Validation du formulaire
    if (!this.validateForm()) {
      return; // Arrêter l'envoi si des erreurs existent
    }

    const student = {
      nom: this.studentLastName,
      prenom: this.studentFirstName,
      site_id: this.studentSiteId,
      promotion_id: this.studentPromotionId,
      semestre_id: this.studentSemestreId,
      groupe_id: this.studentGroupId,
      specialite: this.studentSpecialite,
      //email: this.studentEmail
    };

    fetch('http://localhost:5000/api/etudiants', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(student)
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Étudiant ajouté avec succès:', data);
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'Étudiant ajouté avec succès !' },
        });

        this.dialog.afterAllClosed.subscribe(() => {
          this.router.navigate(['/studentlist']);
        });
      })
      .catch((error) => {
        console.error('Erreur lors de l’ajout de l’étudiant:', error);
      });
  }
}