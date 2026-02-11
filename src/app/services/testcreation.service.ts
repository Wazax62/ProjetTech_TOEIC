import { Injectable } from '@angular/core';

interface Test {
  Titre: string;
  Description: string;
  Site: string;
  Date: string;
}

interface Reponse {
  num_question: string;
  choix: string;
}

@Injectable({
  providedIn: 'root'
})
export class TestCreationService {
  private testData: Test | null = null;
  private reponsesData: Reponse[] = [];
  private selectedGroupes: number[] = [];

  // Stocker le test
  setTestData(test: Test): void {
    this.testData = test;
  }

  // Récupérer le test
  getTestData(): Test | null {
    return this.testData;
  }

  // Stocker les réponses
  setReponses(reponses: Reponse[]): void {
    this.reponsesData = reponses;
  }

  // Récupérer les réponses
  getReponses(): Reponse[] {
    return this.reponsesData;
  }

  // Stocker les groupes sélectionnés
  setSelectedGroupes(groupes: number[]): void {
    this.selectedGroupes = groupes;
  }

  // Récupérer les groupes sélectionnés
  getSelectedGroupes(): number[] {
    return this.selectedGroupes;
  }

  // Ajouter une réponse
  addReponse(reponse: Reponse): void {
    this.reponsesData.push(reponse);
  }

  // Supprimer une réponse
  removeReponse(index: number): void {
    this.reponsesData.splice(index, 1);
  }

  // Ajouter un groupe
  addGroupe(groupeId: number): void {
    if (!this.selectedGroupes.includes(groupeId)) {
      this.selectedGroupes.push(groupeId);
    }
  }

  // Supprimer un groupe
  removeGroupe(groupeId: number): void {
    this.selectedGroupes = this.selectedGroupes.filter(id => id !== groupeId);
  }

  // Vider toutes les données
  clearAll(): void {
    this.testData = null;
    this.reponsesData = [];
    this.selectedGroupes = [];
  }
}