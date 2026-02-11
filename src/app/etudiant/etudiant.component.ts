import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { EtudiantService } from '../etudiant.service';
import { MatDialog } from '@angular/material/dialog';  
import { SuccessDialogComponent } from '../success-dialog/success-dialog.component';
import { NavbarComponent } from '../navbar/navbar.component';


@Component({
  selector: 'app-etudiant',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule,NavbarComponent],
  templateUrl: './etudiant.component.html',
  styleUrls: ['./etudiant.component.css'],
})
export class EtudiantComponent implements OnInit {
  students: any[] = [];
  searchText: string = '';
  currentPage: number = 1;
  itemsPerPage: number = 6;

  constructor(private etudiantService: EtudiantService,private dialog: MatDialog ) {}

  ngOnInit(): void {
    this.loadStudents();
  }

  async loadStudents(): Promise<void> {
    try {
      this.students = await this.etudiantService.getEtudiants();
      console.log('Étudiants chargés avec succès:', this.students);
    } catch (error) {
      console.error('Erreur lors du chargement des étudiants:', error);
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


get filteredStudents() {
    return this.students
      .filter(
        (student) =>
          // Recherche par nom et prénom
          `${student.nom} ${student.prenom}`.toLowerCase().includes(this.searchText.toLowerCase()) ||
          // Recherche par groupe
          student.groupe.toLowerCase().includes(this.searchText.toLowerCase()) ||
          // Recherche par spécialité
          student.specialite.toLowerCase().includes(this.searchText.toLowerCase()) ||
          // Recherche par site
          student.site.toLowerCase().includes(this.searchText.toLowerCase())
      )
      .slice(
        (this.currentPage - 1) * this.itemsPerPage,
        this.currentPage * this.itemsPerPage
      );
  }

 /* get filteredStudents() {
    return this.students
      .filter(
        (student) =>
          student.nom.toLowerCase().includes(this.searchText.toLowerCase()) ||
          student.prenom.toLowerCase().includes(this.searchText.toLowerCase()) ||
          student.groupe.toLowerCase().includes(this.searchText.toLowerCase())
      )
      .slice(
        (this.currentPage - 1) * this.itemsPerPage,
        this.currentPage * this.itemsPerPage
      );
  }
*/
  get totalPages() {
    return Math.ceil(this.students.length / this.itemsPerPage);
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
