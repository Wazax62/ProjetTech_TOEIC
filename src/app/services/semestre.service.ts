import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class SemestreService {
  private apiUrl = 'http://localhost:5000/api/semestres';

  constructor() {}

  // Récupérer tous les semestres
  async getSemestres(): Promise<any[]> {
    try {
      const response = await fetch(this.apiUrl);
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des semestres');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }

  // Récupérer un semestre par son ID
  async getSemestre(id: number): Promise<any> {
    try {
      const response = await fetch(`${this.apiUrl}/${id}`);
      if (!response.ok) {
        throw new Error('Semestre non trouvé');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }

  // Ajouter un nouveau semestre
  async addSemestre(semestre: any): Promise<any> {
    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(semestre),
      });
      if (!response.ok) {
        throw new Error('Erreur lors de l\'ajout du semestre');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }

  // Mettre à jour un semestre
  async updateSemestre(id: number, semestre: any): Promise<any> {
    try {
      const response = await fetch(`${this.apiUrl}/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(semestre),
      });
      if (!response.ok) {
        throw new Error('Erreur lors de la mise à jour du semestre');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }

  // Supprimer un semestre
  async deleteSemestre(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.apiUrl}/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Erreur lors de la suppression du semestre');
      }
    } catch (error) {
      console.error('Erreur:', error);
      throw error;
    }
  }
}