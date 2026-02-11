import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface Test {
  ID_date_groupe: number | null;
  Titre: string;
  Type: string;
  Date: string;
  Description: string;
  groupe: string;
}

@Component({
  selector: 'app-test',
  templateUrl: './test.component.html',
  styleUrls: ['./test.component.css'],
  imports: [FormsModule, CommonModule]
})
export class TestComponent {
  tests: Test[] = [];
  test: Test = { ID_date_groupe: null, Titre: '', Type: '', Date: '', Description: '', groupe: '' };
  questions = Array.from({ length: 200 }, (_, i) => ({ numero: i + 1, reponse: '' }));

  onSubmit() {
    if (this.test.ID_date_groupe === null) {
      this.test.ID_date_groupe = this.generateUniqueId();
      this.tests.push({ ...this.test });
    } else {
      const index = this.tests.findIndex(t => t.ID_date_groupe === this.test.ID_date_groupe);
      if (index !== -1) {
        this.tests[index] = { ...this.test };
      }
    }
    this.resetForm();
  }

  resetForm() {
    this.test = { ID_date_groupe: null, Titre: '', Type: '', Date: '', Description: '', groupe: '' };
  }

  editTest(test: Test) {
    this.test = { ...test };
  }

  deleteTest(id: number) {
    this.tests = this.tests.filter(t => t.ID_date_groupe !== id);
  }

  generateUniqueId(): number {
    return this.tests.length > 0 ? Math.max(...this.tests.map(t => t.ID_date_groupe || 0)) + 1 : 1;
  }

  generateQuestions() {
    this.questions = Array.from({ length: 200 }, (_, i) => ({ numero: i + 1, reponse: '' }));
  }

  saveResponses() {
    console.log('Réponses enregistrées :', this.questions);
  }
}
