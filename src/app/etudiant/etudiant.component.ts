import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { EtudiantService } from '../etudiant.service';
import { MatDialog } from '@angular/material/dialog';  
import { SuccessDialogComponent } from '../success-dialog/success-dialog.component';
import { NavbarComponent } from '../navbar/navbar.component';
import { GroupeService } from '../services/groupe.service';


@Component({
  selector: 'app-etudiant',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, NavbarComponent],
  templateUrl: './etudiant.component.html',
  styleUrls: ['./etudiant.component.css'],
})
export class EtudiantComponent implements OnInit {
  students: any[] = [];
  groupes: any[] = []; // <-- Liste des groupes pour le menu déroulant
  
  searchText: string = '';
  selectedGroupe: string = ''; // <-- Stocke le nom du groupe sélectionné
  
  currentPage: number = 1;
  itemsPerPage: number = 18;

  constructor(
    private etudiantService: EtudiantService,
    private groupeService: GroupeService, // <-- Injection du service
    private dialog: MatDialog 
  ) {}

  ngOnInit(): void {
    this.loadStudents();
    this.loadGroupes(); // <-- Charger les groupes au démarrage
  }

  async loadStudents(): Promise<void> {
    try {
      this.students = await this.etudiantService.getEtudiants();
      console.log('Étudiants chargés avec succès:', this.students);
    } catch (error) {
      console.error('Erreur lors du chargement des étudiants:', error);
    }
  }

  async loadGroupes(): Promise<void> {
    // On récupère les groupes pour alimenter la liste déroulante
    try {
      this.groupes = await this.groupeService.getGroupes();
    } catch (error) {
      console.error('Erreur lors du chargement des groupes:', error);
    }
  }

  deleteStudent(studentId: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer cet étudiant ?')) {
      fetch(`http://localhost:5000/api/etudiants/${studentId}`, {
        method: 'DELETE',
      })
        .then((response) => {
          if (response.ok) {
            console.log('Étudiant supprimé avec succès');
            this.loadStudents();  // Recharger la liste des étudiants après suppression

            // Ouvrir la boîte de dialogue de succès
            this.dialog.open(SuccessDialogComponent, {
              width: '300px',
              data: { message: "L'étudiant a été supprimé avec succès !" },
            });
          } else {
            console.error('Erreur lors de la suppression de l\'étudiant');
          }
        })
        .catch((error) => {
          console.error('Erreur lors de la suppression de l\'étudiant', error);
        });
    }
  }

  // Étape intermédiaire : filtrer la liste globale (recherche texte + liste déroulante)
  get baseFilteredStudents() {
    return this.students.filter((student) => {
      // 1. Filtre par texte (barre de recherche)
      const matchesSearch = 
        `${student.nom} ${student.prenom}`.toLowerCase().includes(this.searchText.toLowerCase()) ||
        student.groupe.toLowerCase().includes(this.searchText.toLowerCase()) ||
        student.specialite.toLowerCase().includes(this.searchText.toLowerCase()) ||
        student.site.toLowerCase().includes(this.searchText.toLowerCase());

      // 2. Filtre par groupe (menu déroulant)
      const matchesGroupe = this.selectedGroupe ? student.groupe === this.selectedGroupe : true;

      return matchesSearch && matchesGroupe;
    });
  }

// Étape finale : appliquer la pagination en comblant les espaces vides
  get filteredStudents() {
    const filtered = this.baseFilteredStudents;
    const total = filtered.length;
    if (total === 0) return [];
    let startIndex = (this.currentPage - 1) * this.itemsPerPage;
    let endIndex = startIndex + this.itemsPerPage;
    if (endIndex > total) {
      endIndex = total;
      startIndex = Math.max(0, total - this.itemsPerPage);
    }

    return filtered.slice(startIndex, endIndex);
  }

  // Le nombre de pages s'adapte dynamiquement selon les filtres
  get totalPages() {
    return Math.ceil(this.baseFilteredStudents.length / this.itemsPerPage) || 1;
  }

  previousPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }
}