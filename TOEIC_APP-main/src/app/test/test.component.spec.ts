import { Component } from '@angular/core';

interface Test {
  ID_date_groupe: number | null;
  Titre: string;
  Type: string;
  Date: string;
  Description: string;
  groupe: string;
}

@Component({
  selector: 'app-test-management',
  templateUrl: './test-management.component.html',
  styleUrls: ['./test-management.component.css']
})
export class TestManagementComponent {
  tests: Test[] = [];
  test: Test = { ID_date_groupe: null, Titre: '', Type: '', Date: '', Description: '', groupe: '' };

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
    return this.tests.length > 0
      ? Math.max(...this.tests.map(t => t.ID_date_groupe || 0)) + 1
      : 1;
  }
}
