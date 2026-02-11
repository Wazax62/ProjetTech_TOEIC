
import { Component, OnInit } from '@angular/core';
import { SemestreService } from '../services/semestre.service';
import { MatDialog } from '@angular/material/dialog';
import { SuccessDialogComponent } from '../success-dialog/success-dialog.component';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../navbar/navbar.component';

@Component({
  selector: 'app-semestre',
  templateUrl: './semestre.component.html',
  imports: [FormsModule, RouterModule, CommonModule, NavbarComponent],
  styleUrls: ['./semestre.component.css'],
  standalone: true
})
export class SemestreComponent implements OnInit {
  semestres: any[] = [];
  searchText: string = '';
  currentPage: number = 1;
  itemsPerPage: number = 6;

  constructor(private semestreService: SemestreService, private dialog: MatDialog) {}

  async ngOnInit(): Promise<void> {
    await this.loadSemestres();
  }

  // Charger les semestres
  async loadSemestres(): Promise<void> {
    try {
      this.semestres = await this.semestreService.getSemestres();
      console.log('Semestres chargés avec succès:', this.semestres);
    } catch (error) {
      console.error('Erreur lors du chargement des semestres:', error);
    }
  }

  // Supprimer un semestre
  async deleteSemestre(semestreId: number): Promise<void> {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce semestre ?')) {
      try {
        await this.semestreService.deleteSemestre(semestreId);
        console.log('Semestre supprimé avec succès');
        await this.loadSemestres(); // Recharger la liste des semestres après suppression

        // Ouvrir la boîte de dialogue de succès
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'Le semestre a été supprimé avec succès !' },
        });
      } catch (error) {
        console.error('Erreur lors de la suppression du semestre', error);
      }
    }
  }

  // Filtrer les semestres
  get filteredSemestres() {
    return this.semestres
      .filter((semestre) =>
        semestre.nom.toLowerCase().includes(this.searchText.toLowerCase()) ||
        semestre.promotion?.toLowerCase().includes(this.searchText.toLowerCase())
      )
      .slice(
        (this.currentPage - 1) * this.itemsPerPage,
        this.currentPage * this.itemsPerPage
      );
  }

  // Calculer le nombre total de pages
  get totalPages() {
    return Math.ceil(this.semestres.length / this.itemsPerPage);
  }

  // Page précédente
  previousPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  // Page suivante
  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }
}