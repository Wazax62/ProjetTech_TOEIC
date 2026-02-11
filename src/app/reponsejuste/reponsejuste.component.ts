import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TestCreationService } from '../services/testcreation.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface ReponseQuestion {
  numero_question: number;
  choix: string;
}

@Component({
  selector: 'app-reponse-juste',
  templateUrl: './reponsejuste.component.html',
  styleUrls: ['./reponsejuste.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule]
})
export class ReponseJusteComponent implements OnInit {
  configQuestions: ReponseQuestion[] = [];

  constructor(
    private testCreationService: TestCreationService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const savedReponses = this.testCreationService.getReponses();
    if (savedReponses.length > 0) {
      // Convert from service format to component format
      this.configQuestions = savedReponses.map(item => ({
        numero_question: parseInt(item.num_question), 
        choix: item.choix
      }));
    } else {
      for (let i = 1; i <= 200; i++) {
        this.configQuestions.push({
          numero_question: i,
          choix: 'A'
        });
      }
    }
  }

  onSaveConfig(): void {
    // Vérification que toutes les questions ont une réponse
    const allQuestionsAnswered = this.configQuestions.every(item => item.choix !== undefined && item.choix !== null && item.choix !== '');
  
    if (!allQuestionsAnswered) {
      alert('Toutes les questions doivent être répondues.');
      return; // Empêche l'enregistrement si une question n'est pas répondue
    }
  
    // Convertir du format du composant au format du service
    const serviceReponses = this.configQuestions.map(item => ({
      num_question: item.numero_question.toString(),
      choix: item.choix
    }));
  
    this.testCreationService.setReponses(serviceReponses);
    alert('Configuration des réponses enregistrée.');
    this.router.navigate(['/test']);
  }
  
}