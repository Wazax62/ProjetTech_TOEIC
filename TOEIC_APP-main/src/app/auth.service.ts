import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
 
  private registerUrl = 'http://127.0.0.1:5000/api/register';  // URL pour l'inscription

  constructor(private http: HttpClient) {}

 
  // Méthode pour l'inscription
  register(userData: any): Observable<any> {
    return this.http.post<any>(this.registerUrl, userData);
  }
}
