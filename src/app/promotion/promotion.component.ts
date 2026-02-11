import { Component, OnInit } from '@angular/core';
import { PromotionService } from '../services/promotion.service';
import { MatDialog } from '@angular/material/dialog';
import { SuccessDialogComponent } from '../success-dialog/success-dialog.component';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../navbar/navbar.component';
@Component({
  selector: 'app-promotion',
  templateUrl: './promotion.component.html',
  imports: [FormsModule,RouterModule,CommonModule,NavbarComponent],
  styleUrls: ['./promotion.component.css'],
})
export class PromotionComponent implements OnInit {
  promotions: any[] = [];
  searchText: string = '';
  currentPage: number = 1;
  itemsPerPage: number = 6;

  constructor(private promotionService: PromotionService, private dialog: MatDialog) {}

  async ngOnInit(): Promise<void> {
    await this.loadPromotions();
  }

  // Charger les promotions
  async loadPromotions(): Promise<void> {
    try {
      this.promotions = await this.promotionService.getPromotions();
      console.log('Promotions chargées avec succès:', this.promotions);
    } catch (error) {
      console.error('Erreur lors du chargement des promotions:', error);
    }
  }

  // Supprimer une promotion
  async deletePromotion(promotionId: number): Promise<void> {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette promotion ?')) {
      try {
        await this.promotionService.deletePromotion(promotionId);
        console.log('Promotion supprimée avec succès');
        await this.loadPromotions(); // Recharger la liste des promotions après suppression

        // Ouvrir la boîte de dialogue de succès
        this.dialog.open(SuccessDialogComponent, {
          width: '300px',
          data: { message: 'La promotion a été supprimée avec succès !' },
        });
      } catch (error) {
        console.error('Erreur lors de la suppression de la promotion', error);
      }
    }
  }

  // Filtrer les promotions
  get filteredPromotions() {
    return this.promotions
      .filter((promotion) =>
        promotion.nom.toLowerCase().includes(this.searchText.toLowerCase())
      )
      .slice(
        (this.currentPage - 1) * this.itemsPerPage,
        this.currentPage * this.itemsPerPage
      );
  }

  // Calculer le nombre total de pages
  get totalPages() {
    return Math.ceil(this.promotions.length / this.itemsPerPage);
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
