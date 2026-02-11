import { RouterLink } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';
import { SuccessDialogComponent } from '../../success-dialog/success-dialog.component';
import { NavbarComponent } from '../../navbar/navbar.component';

@Component({
  selector: 'app-update-student',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink, NavbarComponent],
  templateUrl: './update-student.component.html',
  styleUrls: ['./update-student.component.css']
})
export class UpdateStudentComponent implements OnInit {
  studentId!: string;
  student: any = {
    nom: '',
    prenom: '',
    site_id: '',
    promotion_id: '',
    semestre_id: '',
    groupe_id: '',
    specialite: ''
  };

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

  // Listes filtrées
  filteredPromotions: any[] = [];
  filteredSemestres: any[] = [];
  filteredGroupes: any[] = [];

  // Propriétés pour gérer les erreurs
  errors: any = {};

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    // Load Font Awesome dynamically if not already loaded
    if (!document.querySelector('link[href*="font-awesome"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
      document.head.appendChild(link);
    }
    
    this.studentId = this.route.snapshot.paramMap.get('id')!;
    this.fetchStudentDetails();
    this.fetchSites();
  }

  // Récupérer les détails de l'étudiant
  fetchStudentDetails() {
    fetch(`http://localhost:5000/api/etudiants/${this.studentId}`)
      .then((response) => response.json())
      .then((data) => {
        this.student = data;
        console.log('Student après assignation:', this.student); // Debug
        
        if (this.student.site_id) {
          this.fetchPromotionsBySite(this.student.site_id);
        }
        if (this.student.promotion_id) {
          this.fetchSemestresByPromotion(this.student.promotion_id);
        }
        if (this.student.semestre_id && this.student.promotion_id && this.student.site_id) {
          this.fetchGroupesBySitePromotionSemestre(
            this.student.site_id,
            this.student.promotion_id,
            this.student.semestre_id
          );
        }
      })
      .catch((error) => console.error('Erreur lors de la récupération des détails de l\'étudiant:', error));
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

  // Récupération des promotions par site
  fetchPromotionsBySite(siteId: string) {
    fetch(`http://localhost:5000/api/promotions/by_site/${siteId}`)
      .then((res) => res.json())
      .then((data) => {
        this.filteredPromotions = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des promotions:', error));
  }

  // Récupération des semestres par promotion
  fetchSemestresByPromotion(promotionId: string) {
    fetch(`http://localhost:5000/api/semestres/by_promotion?promotion_id=${promotionId}`)
      .then((res) => res.json())
      .then((data) => {
        this.filteredSemestres = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des semestres:', error));
  }

  // Récupération des groupes par site, promotion et semestre
  fetchGroupesBySitePromotionSemestre(siteId: string, promotionId: string, semestreId: string) {
    const url = `http://localhost:5000/api/groupes/by_site_promotion_semestre?site_id=${siteId}&promotion_id=${promotionId}&semestre_id=${semestreId}`;

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        this.filteredGroupes = data;
      })
      .catch((error) => console.error('Erreur lors du chargement des groupes:', error));
  }

  // Lorsque le site est sélectionné
  onSiteChange(siteId: string) {
    this.student.site_id = siteId;
    this.student.promotion_id = '';
    this.student.semestre_id = '';
    this.student.groupe_id = '';
    this.filteredPromotions = [];
    this.filteredSemestres = [];
    this.filteredGroupes = [];

    if (siteId) {
      this.fetchPromotionsBySite(siteId);
    }
  }

  // Lorsque la promotion est sélectionnée
  onPromotionChange(promotionId: string) {
    this.student.promotion_id = promotionId;
    this.student.semestre_id = '';
    this.student.groupe_id = '';
    this.filteredSemestres = [];
    this.filteredGroupes = [];

    if (promotionId) {
      this.fetchSemestresByPromotion(promotionId);
    }
  }

  // Lorsque le semestre est sélectionné
  onSemestreChange(semestreId: string) {
    this.student.semestre_id = semestreId;
    this.student.groupe_id = '';
    this.filteredGroupes = [];

    if (semestreId && this.student.promotion_id && this.student.site_id) {
      this.fetchGroupesBySitePromotionSemestre(
        this.student.site_id,
        this.student.promotion_id,
        semestreId
      );
    }
  }

  // Méthode pour mettre à jour l'étudiant
  updateStudent() {
    if (!this.validateForm()) {
      return;
    }

    fetch(`http://localhost:5000/api/etudiants/${this.studentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(this.student)
    })
      .then((response) => response.json())
      .then((data) => {
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'Étudiant mis à jour avec succès !' },
        });

        this.dialog.afterAllClosed.subscribe(() => {
          this.router.navigate(['/studentlist']);
        });
      })
      .catch((error) => console.error('Erreur lors de la mise à jour de l\'étudiant:', error));
  }

  // Méthode pour valider le formulaire
  validateForm(): boolean {
    this.errors = {};

    if (!this.student.nom) this.errors['nom'] = 'Le nom est requis.';
    if (!this.student.prenom) this.errors['prenom'] = 'Le prénom est requis.';
    if (!this.student.site_id) this.errors['site_id'] = 'Le site est requis.';
    if (!this.student.promotion_id) this.errors['promotion_id'] = 'La promotion est requise.';
    if (!this.student.semestre_id) this.errors['semestre_id'] = 'Le semestre est requis.';
    if (!this.student.groupe_id) this.errors['groupe_id'] = 'Le groupe est requis.';
    if (!this.student.specialite) this.errors['specialite'] = 'La spécialité est requise.';

    return Object.keys(this.errors).length === 0;
  }

  // Vérifier si tous les champs obligatoires sont remplis
  isFormFilled(): boolean {
    return (
      this.student.nom?.trim() !== '' && 
      this.student.prenom?.trim() !== '' && 
      this.student.site_id !== '' && 
      this.student.promotion_id !== '' && 
      this.student.semestre_id !== '' &&
      this.student.groupe_id !== '' &&
      this.student.specialite !== ''
    );
  }

  // Méthodes pour récupérer les noms des éléments sélectionnés
  getSiteName(siteId: string): string {
    const site = this.sites.find(s => s.id.toString() === siteId.toString());
    return site ? site.nom : '';
  }

  getPromotionName(promotionId: string): string {
    const promotion = this.filteredPromotions.find(p => p.id.toString() === promotionId.toString());
    return promotion ? promotion.nom : '';
  }

  getSemestreName(semestreId: string): string {
    const semestre = this.filteredSemestres.find(s => s.id.toString() === semestreId.toString());
    return semestre ? semestre.nom : '';
  }

  getGroupeName(groupeId: string): string {
    const groupe = this.filteredGroupes.find(g => g.id.toString() === groupeId.toString());
    return groupe ? groupe.nom : '';
  }
}