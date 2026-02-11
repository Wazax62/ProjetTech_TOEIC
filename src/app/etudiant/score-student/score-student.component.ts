import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { HttpClient, HttpParams } from '@angular/common/http';

@Component({
  selector: 'app-score-student',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './score-student.component.html',
  styleUrls: ['./score-student.component.css'],
})
export class ScoreStudentComponent implements OnInit {
  sites: any[] = []; // Liste des sites
  promotions: any[] = []; // Liste des promotions
  groupes: any[] = []; // Liste des groupes
  selectedSiteId: number | null = null; // Site sélectionné
  selectedPromotionId: number | null = null; // Promotion sélectionnée
  selectedSemestreId: number | null = null;
  showTable: boolean = false;
  tests: any[] = []; // Liste des tests
  selectedGroupeId: number | null = null; // Groupe sélectionné
  semestres: any[] = [];
  students: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadSites(); // Charger tous les sites au démarrage
  }

  async showResultsTable(): Promise<void> {
    try {
      const siteId = this.selectedSiteId;
      const promotionId = this.selectedPromotionId;
      const groupeId = this.selectedGroupeId;
      const semestreId = this.selectedSemestreId;
      const testId = (document.getElementById('testFilter') as HTMLSelectElement).value;

      if (!siteId || !promotionId || !groupeId || !semestreId || !testId) {
        alert('Veuillez sélectionner tous les filtres (site, promotion, semestre, groupe et test)');
        return;
      }

      const response = await fetch(
        `http://localhost:5000/api/scores/calculate?site_id=${siteId}&promotion_id=${promotionId}&groupe_id=${groupeId}&semestre_id=${semestreId}&test_id=${testId}`
      );

      if (!response.ok) {
        throw new Error('Erreur lors du calcul des scores');
      }

      this.students = await response.json();
      this.showTable = true;
    } catch (error) {
      console.error('Erreur:', error);
      alert('Une erreur est survenue lors du calcul des scores');
    }
  }

  // Méthode pour télécharger le PDF Oral
  downloadOralPDF(): void {
    if (!this.validateFilters()) return;

    const params = new HttpParams()
      .set('site_id', this.selectedSiteId!.toString())
      .set('promotion_id', this.selectedPromotionId!.toString())
      .set('groupe_id', this.selectedGroupeId!.toString())
      .set('semestre_id', this.selectedSemestreId!.toString())
      .set('test_id', (document.getElementById('testFilter') as HTMLSelectElement).value);

    this.http.get('http://localhost:5000/api/generate-oral-pdf', { 
      params: params,
      responseType: 'blob' as 'json'
    }).subscribe((response: any) => {
      this.downloadFile(response, 'scores_oral.pdf');
    }, error => {
      console.error('Erreur lors du téléchargement du PDF Oral', error);
      alert('Une erreur est survenue lors de la génération du PDF Oral');
    });
  }

  // Méthode pour télécharger le PDF Écrit
  downloadEcritPDF(): void {
    if (!this.validateFilters()) return;

    const params = new HttpParams()
      .set('site_id', this.selectedSiteId!.toString())
      .set('promotion_id', this.selectedPromotionId!.toString())
      .set('groupe_id', this.selectedGroupeId!.toString())
      .set('semestre_id', this.selectedSemestreId!.toString())
      .set('test_id', (document.getElementById('testFilter') as HTMLSelectElement).value);

    this.http.get('http://localhost:5000/api/generate-ecrit-pdf', { 
      params: params,
      responseType: 'blob' as 'json'
    }).subscribe((response: any) => {
      this.downloadFile(response, 'scores_ecrit.pdf');
    }, error => {
      console.error('Erreur lors du téléchargement du PDF Écrit', error);
      alert('Une erreur est survenue lors de la génération du PDF Écrit');
    });
  }

  // Méthode utilitaire pour télécharger un fichier
  private downloadFile(data: Blob, filename: string): void {
    const blob = new Blob([data], { type: 'application/pdf' });
    const downloadUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    link.click();

    // Libérer l'URL après le téléchargement
    setTimeout(() => {
      URL.revokeObjectURL(downloadUrl);
      link.remove();
    }, 100);
  }

  // Validation des filtres
  private validateFilters(): boolean {
    if (!this.selectedSiteId || !this.selectedPromotionId || 
        !this.selectedGroupeId || !this.selectedSemestreId || 
        !(document.getElementById('testFilter') as HTMLSelectElement).value) {
      alert('Veuillez sélectionner tous les filtres (site, promotion, semestre, groupe et test)');
      return false;
    }
    return true;
  }

  // Charger tous les sites
  async loadSites(): Promise<void> {
    try {
      const response = await fetch('http://localhost:5000/api/sites');
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des sites');
      }
      this.sites = await response.json();
    } catch (error) {
      console.error('Erreur:', error);
    }
  }

  // Charger les promotions en fonction du site sélectionné
  async loadPromotionsBySite(siteId: number): Promise<void> {
    try {
      const response = await fetch(`http://localhost:5000/api/promotions/by_site/${siteId}`);
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des promotions');
      }
      this.promotions = await response.json();
    } catch (error) {
      console.error('Erreur:', error);
    }
  }

  // Charger les groupes en fonction de la promotion et du site sélectionnés
  async loadGroupesByPromotionAndSite(promotionId: number, siteId: number): Promise<void> {
    try {
      const response = await fetch(`http://localhost:5000/api/groupes/by_promotion_and_site/${promotionId}/${siteId}`);
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des groupes');
      }
      this.groupes = await response.json();
    } catch (error) {
      console.error('Erreur:', error);
    }
  }

  // Gestion du changement de site
  onSiteChange(event: Event): void {
    const siteId = +(event.target as HTMLSelectElement).value; // Récupérer l'ID du site
    this.selectedSiteId = siteId;
    this.promotions = []; // Réinitialiser les promotions
    this.groupes = []; // Réinitialiser les groupes
    if (siteId) {
      this.loadPromotionsBySite(siteId); // Charger les promotions du site sélectionné
    }
  }

  // Gestion du changement de promotion
  onPromotionChange(event: Event): void {
    const promotionId = +(event.target as HTMLSelectElement).value; // Récupérer l'ID de la promotion
    this.selectedPromotionId = promotionId;
    this.groupes = []; // Réinitialiser les groupes
    this.semestres = []; // Réinitialiser les semestres
    if (promotionId && this.selectedSiteId) {
      this.loadGroupesByPromotionAndSite(promotionId, this.selectedSiteId); // Charger les groupes
      this.loadSemestresByPromotion(promotionId); // Charger les semestres
    }
  }

  // Gestion du changement de semestre
  onSemestreChange(event: Event): void {
    this.selectedSemestreId = +(event.target as HTMLSelectElement).value;
  }

  // Charger les semestres en fonction de la promotion sélectionnée
  async loadSemestresByPromotion(promotionId: number): Promise<void> {
    try {
      const response = await fetch(`http://localhost:5000/api/semestres/by_promotion?promotion_id=${promotionId}`);
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des semestres');
      }
      this.semestres = await response.json();
    } catch (error) {
      console.error('Erreur:', error);
    }
  }

  // Méthode pour exporter le tableau en CSV
  exportTableToCSV(filename: string): void {
    const table = document.getElementById('resultsTable') as HTMLTableElement;
    const rows = table.querySelectorAll('tr');
    const csv: string[] = [];

    // Parcourir chaque ligne
    rows.forEach((row, rowIndex) => {
      const rowData: string[] = [];
      const cols = row.querySelectorAll('td, th');

      // Parcourir chaque cellule
      cols.forEach((col, colIndex) => {
        let cellValue = col.textContent?.trim() || '';

        // Traitement spécial pour la première ligne (en-têtes)
        if (rowIndex === 0) {
          if (cellValue === 'Nom' || cellValue === 'Prénom') {
            // Combiner "Nom" et "Prénom" en une seule colonne "Étudiant"
            if (cellValue === 'Nom') {
              cellValue = 'Étudiant';
            } else {
              return; // Ignorer la colonne "Prénom"
            }
          }
        } else {
          // Pour les lignes de données, combiner "Nom" et "Prénom" dans une seule colonne
          if (colIndex === 0) {
            // Récupérer le nom et le prénom
            const nom = col.textContent?.trim() || '';
            const prenom = cols[1].textContent?.trim() || '';
            cellValue = `${nom} ${prenom}`;
          } else if (colIndex === 1) {
            return; // Ignorer la colonne "Prénom" après l'avoir combinée
          }
        }

        // Ajouter la valeur de la cellule au tableau
        rowData.push(`"${cellValue.replace(/"/g, '""')}"`);
      });

      // Ajouter la ligne au CSV
      csv.push(rowData.join(','));
    });

    // Créer le fichier CSV et le télécharger
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
  }

  // Charger les tests dynamiquement en fonction du site, promotion et groupe sélectionnés
  async loadTestsBySitePromotionGroupSemester(
    siteId: number, 
    promotionId: number, 
    groupeId: number,
    semestreId: number
  ): Promise<void> {
    try {
      const response = await fetch(
        `http://localhost:5000/api/tests/by_site_promotion_group_semester/${siteId}/${promotionId}/${groupeId}/${semestreId}`
      );
      if (!response.ok) throw new Error('Erreur serveur');
      this.tests = await response.json();
    } catch (error) {
      console.error('Erreur:', error);
      this.tests = []; // Réinitialiser en cas d'erreur
    }
  }

  // Gestion du changement de groupe
  onGroupeChange(event: Event): void {
    const groupeId = +(event.target as HTMLSelectElement).value;
    this.selectedGroupeId = groupeId;
    this.tests = []; // Réinitialiser les tests
    if (this.selectedSiteId && this.selectedPromotionId && groupeId && this.selectedSemestreId) {
      this.loadTestsBySitePromotionGroupSemester(
        this.selectedSiteId, 
        this.selectedPromotionId, 
        groupeId,
        this.selectedSemestreId
      );
    }
  }
}