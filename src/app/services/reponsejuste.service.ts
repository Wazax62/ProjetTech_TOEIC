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
}
