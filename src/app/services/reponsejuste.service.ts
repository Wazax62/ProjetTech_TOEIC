import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ReponseJuste } from '../models/reponse-juste.model';

@Injectable({
  providedIn: 'root'
})
export class ReponseJusteService {
  private apiUrl = 'http://127.0.0.1:5000/api/reponses_justes';

  constructor(private http: HttpClient) {}

  createReponsesBatch(reponses: ReponseJuste[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/batch`, reponses);
  }

  // NOUVEAU : Récupérer les réponses d'un test spécifique
  getReponsesByTestId(testId: string | number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/test/${testId}`);
  }

  // NOUVEAU : Écraser les réponses existantes
  updateReponses(testId: string | number, reponses: any[]): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/test/${testId}`, reponses);
  }
}