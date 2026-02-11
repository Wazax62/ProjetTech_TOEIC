import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { TestGroupe } from '../models/test_groupe.model';


@Injectable({
  providedIn: 'root'
})
export class TestGroupeService {
  private apiUrl = 'http://127.0.0.1:5000/api/tests_groupes';

  constructor(private http: HttpClient) {}

  // Récupère la liste de tous les TestGroupe
  getTestsGroupes(): Observable<TestGroupe[]> {
    return this.http.get<TestGroupe[]>(this.apiUrl + '/');
  }

  // Crée un nouveau TestGroupe
  createTestGroupe(tg: TestGroupe): Observable<any> {
    return this.http.post<any>(this.apiUrl + '/', tg);
  }

  // Récupère un TestGroupe par son id_test
  getTestGroupeById(id_test: number): Observable<TestGroupe> {
    return this.http.get<TestGroupe>(`${this.apiUrl}/${id_test}`);
  }

  // Met à jour un TestGroupe existant
  updateTestGroupe(id_test: number, tg: TestGroupe): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${id_test}`, tg);
  }

  // Supprime un TestGroupe
  deleteTestGroupe(id_test: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id_test}`);
  }
}
