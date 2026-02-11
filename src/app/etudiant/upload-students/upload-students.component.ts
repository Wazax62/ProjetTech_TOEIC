import { Component } from '@angular/core';
import { NgIf } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../navbar/navbar.component';

@Component({
  selector: 'app-upload-students',
  standalone: true,
  imports: [NgIf,FormsModule, CommonModule,ReactiveFormsModule, NavbarComponent],
  templateUrl: './upload-students.component.html',
  styleUrls: ['./upload-students.component.css']
})
export class UploadStudentsComponent {
  selectedFile: File | null = null;
  isLoading: boolean = false;

  constructor() {}

  onFileChange(event: any): void {
    console.log('Événement change détecté', event);

    if (event.target.files.length > 0) {
      this.selectedFile = event.target.files[0];
      console.log('Fichier sélectionné:', this.selectedFile);
    } else {
      console.log("Aucun fichier sélectionné");
    }
  }

  onSubmit(): void {
    console.log('onSubmit appelé');
    if (this.selectedFile) {
      this.isLoading = true;
      const formData = new FormData();
      formData.append('file', this.selectedFile);

      console.log('Envoi du fichier:', this.selectedFile.name);

      fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData
      })
      .then(response => {
        this.isLoading = false;
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Erreur lors du téléversement');
        }
      })
      .then(data => {
        console.log('Fichier téléversé avec succès', data);
        alert('Fichier téléversé avec succès !');
      })
      .catch(error => {
        console.error('Erreur lors du téléversement', error);
        alert('Erreur lors du téléversement du fichier.');
      });
    } else {
      alert('Veuillez sélectionner un fichier.');
    }
  }
}
