import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { TestCreationService } from '../services/testcreation.service';
import { NavbarComponent } from '../navbar/navbar.component';

interface Groupe {
  id_groupe: number;
  nom: string;
  promotion: string;
  site: string;
  semestre: string;
  nombre_tests: number;
  nombre_etudiants: number;
  selected: boolean;
}

@Component({
  selector: 'app-test-groupe',
  templateUrl: './test-groupe.component.html',
  styleUrls: ['./test-groupe.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, NavbarComponent]
})
export class TestGroupeComponent implements OnInit {
 
  searchTerm: string = '';
  groupes: Groupe[] = [];
  
  constructor(
    private http: HttpClient, 
    private router: Router,
    private testCreationService: TestCreationService
  ) {}

  ngOnInit(): void {
    this.fetchGroupes();
    
  }
// Méthode pour récupérer les groupes depuis l'API Flask
fetchGroupes() {
  // Récupérer le site_id à partir du service
  const siteId = this.testCreationService.getTestData()?.Site;
  console.log(siteId)

  // Préparer l'URL de la requête avec site_id si disponible
  let url = 'http://localhost:5000/api/groupesachraf';
  if (siteId) {
    url += `?site_id=${siteId}`; // Ajouter le site_id à l'URL de la requête
  }

  this.http.get<any[]>(url).subscribe(
    (data) => {
      this.groupes = data.map(item => ({
        ...item,
        selected: false
      }));
      // Charger les groupes sélectionnés depuis le service
      this.loadSelectedGroupes();
      console.log('Groupes récupérés:', this.groupes);
    },
    (error) => {
      console.error('Erreur lors de la récupération des groupes', error);
    }
  );
}

  // Méthode pour charger les groupes sélectionnés depuis le service
  loadSelectedGroupes() {
    const selectedIds = this.testCreationService.getSelectedGroupes();
    this.groupes.forEach(groupe => {
      groupe.selected = selectedIds.includes(groupe.id_groupe);
    });
  }
  
  get filteredGroupes() {
    if (!this.searchTerm) return this.groupes;
    return this.groupes.filter(g =>
      g.nom.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }
  
  get selectedGroupCount(): number {
    return this.groupes.filter(g => g.selected).length;
  }

  onSubmitSelection() {
    // Récupérer les IDs des groupes sélectionnés
    const selectedGroupes = this.groupes.filter(g => g.selected);
    const selectedIds = selectedGroupes.map(g => g.id_groupe);
    console.log('Groupes sélectionnés:', selectedGroupes);
    console.log('IDs à enregistrer:', selectedIds);
    
    // Stocker les IDs des groupes sélectionnés dans le service
    this.testCreationService.setSelectedGroupes(selectedIds);
    
    // Rediriger vers la page de test
    this.router.navigate(['/test']);
  }
}