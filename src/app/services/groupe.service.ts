import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class GroupeService {
  private apiUrl = 'http://localhost:5000/api/groupes';

  constructor() {}

  // Récupérer tous les groupes
  async getGroupes(): Promise<any[]> {
    try {
      const response = await fetch(this.apiUrl);
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des groupes');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }

  // Ajouter un nouveau groupe
  async addGroupe(groupe: any): Promise<any> {
    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(groupe),
      });
      if (!response.ok) {
        throw new Error('Erreur lors de l\'ajout du groupe');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }

  // Supprimer un groupe
  async deleteGroupe(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.apiUrl}/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Erreur lors de la suppression du groupe');
      }
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }
}
