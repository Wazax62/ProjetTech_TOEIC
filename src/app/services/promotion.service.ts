import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class PromotionService {
  private apiUrl = 'http://localhost:5000/api/promotions';

  constructor() {}

  // Récupérer toutes les promotions
  async getPromotions(): Promise<any[]> {
    try {
      const response = await fetch(this.apiUrl);
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des promotions');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }

  // Récupérer une promotion par son ID
  async getPromotion(id: number): Promise<any> {
    try {
      const response = await fetch(`${this.apiUrl}/${id}`);
      if (!response.ok) {
        throw new Error('Promotion non trouvée');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }

  // Ajouter une nouvelle promotion
  async addPromotion(promotion: any): Promise<any> {
    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(promotion),
      });
      if (!response.ok) {
        throw new Error('Erreur lors de l\'ajout de la promotion');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }

  // Mettre à jour une promotion
  async updatePromotion(id: number, promotion: any): Promise<any> {
    try {
      const response = await fetch(`${this.apiUrl}/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(promotion),
      });
      if (!response.ok) {
        throw new Error('Erreur lors de la mise à jour de la promotion');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }

  // Supprimer une promotion
  async deletePromotion(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.apiUrl}/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Erreur lors de la suppression de la promotion');
      }
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }
}