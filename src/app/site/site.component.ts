import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { SuccessDialogComponent } from '../success-dialog/success-dialog.component';
import { SiteService } from '../services/site.service';
import { NavbarComponent } from '../navbar/navbar.component';

@Component({
  selector: 'app-site',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, NavbarComponent],
  templateUrl: './site.component.html',
  styleUrls: ['./site.component.css'],
})
export class SiteComponent implements OnInit {
  sites: any[] = [];
  searchText: string = '';
  currentPage: number = 1;
  itemsPerPage: number = 5;

  constructor(private siteService: SiteService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.loadSites();
  }

  async loadSites(): Promise<void> {
    try {
      this.sites = await this.siteService.getSites();
      console.log('Sites chargés avec succès:', this.sites);
    } catch (error) {
      console.error('Erreur lors du chargement des sites:', error);
    }
  }

  async deleteSite(siteId: number): Promise<void> {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce site ?')) {
      try {
        await this.siteService.deleteSite(siteId);
        console.log('Site supprimé avec succès');
        this.loadSites(); // Recharger la liste des sites après suppression

        // Ouvrir la boîte de dialogue de succès
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'Le site a été supprimé avec succès !' },
        });
      } catch (error) {
        console.error('Erreur lors de la suppression du site', error);
      }
    }
  }

  get filteredSites() {
    return this.sites
      .filter((site) =>
        site.nom.toLowerCase().includes(this.searchText.toLowerCase())
      )
      .slice(
        (this.currentPage - 1) * this.itemsPerPage,
        this.currentPage * this.itemsPerPage
      );
  }

  get totalPages() {
    return Math.ceil(this.sites.length / this.itemsPerPage);
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