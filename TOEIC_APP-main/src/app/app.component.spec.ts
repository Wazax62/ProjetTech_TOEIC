<<<<<<< HEAD
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';



interface Test {
  ID_date_groupe: number | null; // Permet `null` temporairement
  Titre: string;
  Type: string;
  Date: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

class AppComponent {
  tests: Test[] = []; // Liste des tests
  test: Test = { ID_date_groupe: null, Titre: '', Type: '', Date: '' }; // Nouveau test
  selectedFile: File | null = null; // Fichier PDF
  uploadResponse: any = null; // Réponse après téléchargement de PDF

  // Ajouter un nouveau test
  addTest() {
    if (this.test.ID_date_groupe === null) {
      this.test.ID_date_groupe = this.generateUniqueId(); // Génère un ID unique
    }
    this.tests.push({ ...this.test }); // Ajoute le test à la liste
    this.test = { ID_date_groupe: null, Titre: '', Type: '', Date: '' }; // Réinitialise le formulaire
  }

  // Supprimer un test
  deleteTest(index: number) {
    this.tests.splice(index, 1);
  }

  // Gérer le fichier PDF sélectionné
  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  // Télécharger et traiter un fichier PDF
  uploadPDF() {
    if (this.selectedFile) {
      const formData = new FormData();
      formData.append('file', this.selectedFile);

      // Simuler une réponse après le traitement
      this.uploadResponse = { message: 'PDF téléchargé et analysé avec succès !' };
      console.log('PDF traité :', this.selectedFile.name);
    }
  }

  // Générer un ID unique pour chaque test
  generateUniqueId(): number {
    return this.tests.length > 0
      ? Math.max(...this.tests.map(t => t.ID_date_groupe || 0)) + 1
      : 1;
  }
}
=======
// import { Component } from '@angular/core';
// import { FormsModule } from '@angular/forms';
// import { CommonModule } from '@angular/common';



// interface Test {
//   ID_date_groupe: number | null; // Permet `null` temporairement
//   Titre: string;
//   Type: string;
//   Date: string;
// }

// @Component({
//   selector: 'app-root',
//   standalone: true,
//   imports: [FormsModule, CommonModule],
//   templateUrl: './app.component.html',
//   styleUrls: ['./app.component.css']
// })

// class AppComponent {
//   tests: Test[] = []; // Liste des tests
//   test: Test = { ID_date_groupe: null, Titre: '', Type: '', Date: '' }; // Nouveau test
//   selectedFile: File | null = null; // Fichier PDF
//   uploadResponse: any = null; // Réponse après téléchargement de PDF

//   // Ajouter un nouveau test
//   addTest() {
//     if (this.test.ID_date_groupe === null) {
//       this.test.ID_date_groupe = this.generateUniqueId(); // Génère un ID unique
//     }
//     this.tests.push({ ...this.test }); // Ajoute le test à la liste
//     this.test = { ID_date_groupe: null, Titre: '', Type: '', Date: '' }; // Réinitialise le formulaire
//   }

//   // Supprimer un test
//   deleteTest(index: number) {
//     this.tests.splice(index, 1);
//   }

//   // Gérer le fichier PDF sélectionné
//   onFileSelected(event: any) {
//     this.selectedFile = event.target.files[0];
//   }

//   // Télécharger et traiter un fichier PDF
//   uploadPDF() {
//     if (this.selectedFile) {
//       const formData = new FormData();
//       formData.append('file', this.selectedFile);

//       // Simuler une réponse après le traitement
//       this.uploadResponse = { message: 'PDF téléchargé et analysé avec succès !' };
//       console.log('PDF traité :', this.selectedFile.name);
//     }
//   }

//   // Générer un ID unique pour chaque test
//   generateUniqueId(): number {
//     return this.tests.length > 0
//       ? Math.max(...this.tests.map(t => t.ID_date_groupe || 0)) + 1
//       : 1;
//   }
// }
>>>>>>> safa_branch
