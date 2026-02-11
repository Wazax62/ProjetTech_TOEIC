import { CommonModule } from '@angular/common';
import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

interface StudentResult {
  nom: string;
  prenom: string;
  oralScore: number;
  writtenScore: number;
  totalScore: number;
  ccNote: number;
  ecueNote: number;
}

@Component({
  selector: 'app-reponseetudiant',
  templateUrl: './reponseetudiant.component.html',
  styleUrls: ['./reponseetudiant.component.css'],
  imports: [FormsModule, CommonModule,  RouterModule]
})
export class ReponseEtudiantComponent implements OnInit {
  // Propriété pour le fichier PDF importé
  pdfFile: File | null = null;
  // Flag pour gérer l'état "drag over"
  dragOver: boolean = false;
  // Exemple de résultats pour simuler l'affichage
  results: StudentResult[] = [];

  @ViewChild('fileInput') fileInput!: ElementRef;

  ngOnInit(): void {
    // Exemple de résultats (données fictives)
    this.results = [
      { nom: 'Dupont', prenom: 'Jean', oralScore: 400, writtenScore: 420, totalScore: 820, ccNote: 15, ecueNote: 16 },
      { nom: 'Martin', prenom: 'Claire', oralScore: 380, writtenScore: 410, totalScore: 790, ccNote: 14, ecueNote: 15 },
      { nom: 'Durand', prenom: 'Paul', oralScore: 420, writtenScore: 430, totalScore: 850, ccNote: 17, ecueNote: 18 }
    ];
  }

  // Méthode pour gérer le survol (dragover)
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = true;
  }

  // Méthode pour gérer le dragleave
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = false;
  }

  // Méthode pour gérer le dépôt de fichier (drop)
  onFileDropped(event: DragEvent): void {
    event.preventDefault();
    this.dragOver = false;
    if (event.dataTransfer && event.dataTransfer.files.length > 0) {
      this.pdfFile = event.dataTransfer.files[0];
      console.log("Fichier déposé :", this.pdfFile);
      alert("Fichier PDF sélectionné : " + this.pdfFile.name);
      // Vous pouvez ajouter ici la logique pour traiter le PDF et mettre à jour les résultats
    }
  }

  // Méthode pour gérer la sélection via l'input file
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.pdfFile = input.files[0];
      console.log("Fichier sélectionné :", this.pdfFile);
      alert("Fichier PDF sélectionné : " + this.pdfFile.name);
      // Ajoutez ici la logique pour traiter le PDF et mettre à jour les résultats
    }
  }

  // Déclenche le clic sur l'input caché
  triggerFileInput(): void {
    this.fileInput.nativeElement.click();
  }
}
