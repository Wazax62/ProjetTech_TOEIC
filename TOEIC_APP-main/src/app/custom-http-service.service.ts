import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http'; // Import HttpClient
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root', // This ensures it's available globally
})
export class CustomHttpServiceService {
  constructor(private http: HttpClient) {}

  registerUser(user: any): Observable<any> {
    return this.http.post('http://localhost:5000/api/register', user);
  }
}
