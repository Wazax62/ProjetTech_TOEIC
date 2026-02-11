import { CommonModule } from '@angular/common';
import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NavbarComponent } from '../navbar/navbar.component';


interface TestGroupe {
  test_id: number;
  test_title: string;
  test_date: string;
  test_description: string;
  groupe_id: number;
  groupe_name: string;
  feuille_generee: boolean;
}

@Component({
  selector: 'app-evaluations',
  templateUrl: './evaluations.component.html',
  styleUrls: ['./evaluations.component.css'],
  imports: [FormsModule, CommonModule, NavbarComponent]
})
export class EvaluationsComponent implements OnInit {

  testsAndGroups: TestGroupe[] = [];
  searchTerm: string = '';
  isLoading: boolean = false;
  loadingButtonId: string | null = null;

  // Variables pour la correction (upload PDF)
  showModal = false;
  selectedEvaluation: any;  // L'évaluation sur laquelle on corrige

  // Variables pour la duplication
  showDuplicateModal = false;

  // Formulaire de duplication
  duplicateForm = {
    nom: '',
    description: '',
    date: '',
    site_id: null as number|null,
    promotions_ids: [] as number[],
    groupes_ids: [] as number[],
    copyReponsesProf: true
  };

  // Listes pour alimenter les <select> Site / Promotion / Groupe
  sites: any[] = [];
  promotions: any[] = [];
  groupes: any[] = [];

  constructor(
    private router: Router
  ) {}

  ngOnInit(): void {
    this.getTestsAndGroups();
    this.fetchSites();
    this.fetchPromotions();
    this.fetchGroupes();
  }

  // 1) Charger la liste Tests/Groupe
  getTestsAndGroups(): void {
    fetch('http://localhost:5000/api/evaluations')
      .then(response => response.json())
      .then(data => {
        this.testsAndGroups = data;
      })
      .catch(error => console.error('Error fetching tests and groups:', error));
  }

  // 2) Filtrer les évaluations
  get filteredEvaluations(): TestGroupe[] {
    if (!this.searchTerm.trim()) {
      return this.testsAndGroups;
    }
    return this.testsAndGroups.filter(item =>
      item.test_title.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  // 3) Télécharger la feuille de réponse
  viewResponseSheet(testId: number, groupeId: number) {
    this.loadingButtonId = `btn-${testId}-${groupeId}`;
    this.router.navigate(['/impression', testId, groupeId]);
    setTimeout(() => {
      this.loadingButtonId = null;
    }, 500);
  }

  // 4) Ouvrir la modale de Correction
  openUploadModal(evaluation: any) {
    this.selectedEvaluation = evaluation;
    this.showModal = true;
  }

  // 5) Gestion de l'upload PDF
  onFileChange(event: any) {
    const file = event.target.files[0];
    // ...
  }
  onSubmit() {
    if (!this.isLoading) {
      this.isLoading = true;
      setTimeout(() => {
        this.isLoading = false;
      }, 2000);
    }
  }
  uploadPdf(testId: string, groupeId: string): void {
    this.isLoading = true;
    if (!testId || !groupeId) {
      alert('test_id et groupe_id requis');
      this.isLoading = false;
      return;
    }
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = fileInput?.files?.[0];
    if (!file) {
      alert('Veuillez sélectionner un fichier PDF');
      this.isLoading = false;
      return;
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Veuillez sélectionner un fichier PDF valide');
      this.isLoading = false;
      return;
    }
    const formData = new FormData();
    formData.append('pdf_file', file);
    formData.append('test_id', testId);
    formData.append('groupe_id', groupeId);

    fetch('http://localhost:5000/api/process-pdf', {
      method: 'POST',
      body: formData,
    })
    .then(response => response.json().then(data => {
      if (!response.ok) {
        throw new Error(data.error || `Erreur HTTP: ${response.status}`);
      }
      return data;
    }))
    .then((data: { message: string; saved_count: number; student_count: number }) => {
      alert(`${data.message}\nRéponses enregistrées: ${data.saved_count} pour ${data.student_count} étudiants.`);
      if (fileInput) fileInput.value = '';
    })
    .catch(error => {
      console.error('Erreur:', error);
      alert(`Erreur: ${error.message}`);
    })
    .finally(() => {
      this.isLoading = false;
    });
  }

  // 6) Supprimer
  deleteEvaluation(id: number): void {
    if (!confirm("Voulez-vous vraiment supprimer ce test ?")) {
      return;
    }
  
    // Appel HTTP DELETE vers l’API
    fetch(`http://localhost:5000/api/evaluations/${id}`, {
      method: 'DELETE'
    })
    .then((response) => {
      // Vérifier si la requête a réussi
      if (!response.ok) {
        throw new Error(`Erreur suppression: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log(data.message);
  
      // Si succès, on retire localement le test
      this.testsAndGroups = this.testsAndGroups.filter(e => e.test_id !== id);
      alert("Test supprimé avec succès !");
    })
    .catch((err) => {
      console.error("Erreur lors de la suppression:", err);
      alert("Une erreur est survenue lors de la suppression du test.");
    });
  }

  // =========================================================
  // DUPLICATION
  // =========================================================
  
  // 7) Ouvrir la modale de duplication
  openDuplicateModal(evaluation: any) {
    this.showDuplicateModal = true;
    // Préremplir le formulaire
    this.duplicateForm.nom = evaluation.test_title + ' (Copie)';
    this.duplicateForm.description = evaluation.test_description || '';
    this.duplicateForm.date = '';  // Laisser l’utilisateur choisir
    this.duplicateForm.site_id = null;
    this.duplicateForm.promotions_ids = [];
    this.duplicateForm.groupes_ids = [];
    this.duplicateForm.copyReponsesProf = true;

    // Mémoriser l'id du test d'origine si besoin
    this.selectedEvaluation = evaluation;
  }

  submitDuplicateForm() {
    if (!this.selectedEvaluation) return;

    // Créer le payload
    const payload = {
      nom: this.duplicateForm.nom,
      description: this.duplicateForm.description,
      date: this.duplicateForm.date,
      site_id: this.duplicateForm.site_id,
      promotions_ids: this.duplicateForm.promotions_ids,
      groupes_ids: this.duplicateForm.groupes_ids,
      copyReponsesProf: this.duplicateForm.copyReponsesProf
    };

    const oldTestId = this.selectedEvaluation.test_id;

    fetch(`http://localhost:5000/api/evaluations/duplicate/${oldTestId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      if (!data.new_test_id) {
        throw new Error("Impossible de dupliquer le test");
      }
      alert(`Test dupliqué avec succès ! ID = ${data.new_test_id}`);
      // Option : recharger la liste
      this.getTestsAndGroups();

      // Fermer la modale
      this.showDuplicateModal = false;
    })
    .catch(err => {
      console.error("Erreur duplication:", err);
      alert("Une erreur est survenue lors de la duplication.");
    });
  }

  // =========================================================
  // Charger la liste des sites, promos, groupes
  // =========================================================
  fetchSites() {
    fetch('http://localhost:5000/api/sites')
      .then(res => res.json())
      .then(data => this.sites = data)
      .catch(err => console.error(err));
  }

  fetchPromotions() {
    fetch('http://localhost:5000/api/promotions')
      .then(res => res.json())
      .then(data => this.promotions = data)
      .catch(err => console.error(err));
  }

  fetchGroupes() {
    fetch('http://localhost:5000/api/groupes')
      .then(res => res.json())
      .then(data => this.groupes = data)
      .catch(err => console.error(err));
  }

}
