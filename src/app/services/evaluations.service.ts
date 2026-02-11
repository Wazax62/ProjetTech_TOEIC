// src/app/services/evaluation.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '../auth.service';

@Injectable({
  providedIn: 'root'
})
export class EvaluationsService {

  private baseUrl = 'http://localhost:5000/api'; // URL backend

  constructor(private http: HttpClient, private authService: AuthService) { }

  // Méthode pour récupérer les évaluations
  getEvaluations(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/evaluations`, 
      { headers: this.authService.getAuthHeaders() });
  }

  // Méthode pour dupliquer un test
  duplicateTest(oldTestId: number, payload: any): Observable<any> {
    // payload peut contenir { nom, description, groupes_ids, ... }
    return this.http.post(`${this.baseUrl}/tests/duplicate/${oldTestId}`, payload, 
      { headers: this.authService.getAuthHeaders() });
  }

  // Méthode pour supprimer un test
  deleteTest(testId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/tests/${testId}`, 
      { headers: this.authService.getAuthHeaders() });
  }
}
