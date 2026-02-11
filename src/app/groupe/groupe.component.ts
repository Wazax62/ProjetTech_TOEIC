import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { SuccessDialogComponent } from '../success-dialog/success-dialog.component';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { GroupeService } from '../services/groupe.service';
import { NavbarComponent } from '../navbar/navbar.component';

@Component({
  selector: 'app-groupe',
  templateUrl: './groupe.component.html',
  styleUrls: ['./groupe.component.css'],
  imports: [FormsModule, RouterModule, CommonModule,NavbarComponent],
})
export class GroupeComponent implements OnInit {
  groupes: any[] = [];
  searchText: string = '';
  currentPage: number = 1;
  itemsPerPage: number = 6;

  constructor(private groupeService: GroupeService, private dialog: MatDialog) {}

  async ngOnInit(): Promise<void> {
    await this.loadGroupes();
  }

  // Charger les groupes
  async loadGroupes(): Promise<void> {
    try {
      this.groupes = await this.groupeService.getGroupes();
      console.log('Groupes chargés avec succès:', this.groupes);
    } catch (error) {
      console.error('Erreur lors du chargement des groupes:', error);
    }
  }

  // Supprimer un groupe
  async deleteGroupe(groupeId: number): Promise<void> {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce groupe ?')) {
      try {
        await this.groupeService.deleteGroupe(groupeId);
        console.log('Groupe supprimé avec succès');
        await this.loadGroupes(); // Recharger la liste des groupes après suppression

        // Ouvrir la boîte de dialogue de succès
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'Le groupe a été supprimé avec succès !' },
        });
      } catch (error) {
        console.error('Erreur lors de la suppression du groupe', error);
      }
    }
  }

  // Filtrer les groupes
  get filteredGroupes() {
    return this.groupes
      .filter((groupe) =>
        groupe.nom.toLowerCase().includes(this.searchText.toLowerCase()) ||
        groupe.site.toLowerCase().includes(this.searchText.toLowerCase())
      )
      .slice(
        (this.currentPage - 1) * this.itemsPerPage,
        this.currentPage * this.itemsPerPage
      );
  }

  // Calculer le nombre total de pages
  get totalPages() {
    return Math.ceil(this.groupes.length / this.itemsPerPage);
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
