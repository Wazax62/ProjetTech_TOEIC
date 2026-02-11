import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class SiteService {
  private apiUrl = 'http://127.0.0.1:5000/api/sites';

  constructor() {}

  async getSites(): Promise<any[]> {
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
      console.error('Erreur lors de la récupération des sites:', error);
      throw error;
    }
  }
////
  async createSite(site: any): Promise<any> {
    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(site),
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP : ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la création du site:', error);
      throw error;
    }
  }

  async deleteSite(siteId: number): Promise<void> {
    try {
      const response = await fetch(`${this.apiUrl}/${siteId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP : ${response.status}`);
      }
    } catch (error) {
      console.error('Erreur lors de la suppression du site:', error);
      throw error;
    }
  }
}