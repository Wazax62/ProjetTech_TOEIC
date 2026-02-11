import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class EtudiantService {
  private apiUrl = 'http://127.0.0.1:5000/api/etudiants';

  constructor() {}

  async getEtudiants(): Promise<any[]> {
    try {
      const response = await fetch(this.apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP : ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la récupération des étudiants:', error);
      throw error;
    }
  }

  
}
