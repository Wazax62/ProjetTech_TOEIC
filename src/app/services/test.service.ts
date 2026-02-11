import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Test } from '../models/test.model';

@Injectable({
  providedIn: 'root'
})
export class TestService {
  private apiUrl = 'http://127.0.0.1:5000/api/tests';

  constructor(private http: HttpClient) {}

  createTest(testData: Test): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/`, testData);
  }
  
  // Autres méthodes (getTests, updateTest, deleteTest) si besoin...
}
