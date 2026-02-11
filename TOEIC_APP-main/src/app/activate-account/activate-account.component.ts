import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-activate-account', 
  templateUrl: './activate-account.component.html',  
  styleUrls: ['./activate-account.component.css'],   
  imports: [FormsModule,CommonModule], 
})
export class ActivateAccountComponent implements OnInit {
  statusMessage: string = '';
  messageType: string = ''; 

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    const token = this.route.snapshot.paramMap.get('token');  
    if (token) {
      this.activateAccount(token);
    }
  }

  activateAccount(token: string) {
    fetch(`http://127.0.0.1:5000/api/activate/${token}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          this.statusMessage = 'Votre compte a été activé avec succès.';
          this.messageType = 'success';
        } else {
          this.statusMessage = data.message;
          this.messageType = 'error';
        }
      })
      .catch((error) => {
        this.statusMessage = 'Une erreur est survenue lors de l\'activation du compte.';
        this.messageType = 'error';
      });
  }
}
