import { Routes, Router } from '@angular/router';
import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

// Imports des composants
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { ActivateAccountComponent } from './activate-account/activate-account.component';
import { TestComponent } from './test/test.component';
import { HomeComponent } from './home/home.component';
import { EvaluationsComponent } from './evaluations/evaluations.component';
import { ReponseEtudiantComponent } from './reponseetudiant/reponseetudiant.component';
import { ReponseJusteComponent } from './reponsejuste/reponsejuste.component';
import { TestGroupeComponent } from './test-groupe/test-groupe.component';
import { EtudiantComponent } from './etudiant/etudiant.component';
import { UpdateStudentComponent } from './etudiant/update-student/update-student.component';
import { ScoreStudentComponent } from './etudiant/score-student/score-student.component';
import { AddstudentComponent } from './etudiant/addstudent/addstudent.component';
import { UploadStudentsComponent } from './etudiant/upload-students/upload-students.component';
import { SiteComponent } from './site/site.component';
import { PromotionComponent } from './promotion/promotion.component';
import { GroupeComponent } from './groupe/groupe.component';
import { AddGroupComponent } from './groupe/addgroupe/addgroup/addgroup.component';
import { UpdateGroupComponent } from './groupe/updategroupe/updategroup/updategroup.component';
import { AddPromoComponent } from './promotion/addPromo/add-promo/add-promo.component';
import { UpdatePromoComponent } from './promotion/updatePromo/update-promo/update-promo.component';
import { AddSiteComponent } from './site/addsite/add-site/add-site.component';
import { ScoreComponent } from './score/score.component';
import { SemestreComponent } from './semestre/semestre.component';
import { AddSemestreComponent } from './semestre/add-semestre/add-semestre.component';
import { UpdateSemestreComponent } from './semestre/update-semestre/update-semestre.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  
  // Route par défaut (Home)
  { 
    path: '', 
    loadComponent: () => import('./home/home.component').then(m => m.HomeComponent),
    canActivate: [() => {
      const platformId = inject(PLATFORM_ID);
      const router = inject(Router);
      
      if (isPlatformBrowser(platformId)) {
        // Remplacez 'token' par le bon nom si nécessaire (ex: 'access_token')
        const token = localStorage.getItem('token');
        if (!token) {
          return router.createUrlTree(['/login']);
        }
        return true;
      }
      return true; 
    }]
  },

  // Autres routes
  { path: 'activate-account/:token', component: ActivateAccountComponent },
  { path: 'test', component: TestComponent },
  { path: 'home', component: HomeComponent },
  { path: 'evaluations', component: EvaluationsComponent },
  { path: 'classes', component: TestGroupeComponent },
  { path: 'reponseetudiant', component: ReponseEtudiantComponent },
  { path: 'reponsejuste', component: ReponseJusteComponent },
  { path: 'studentlist', component: EtudiantComponent },
  { path: 'update-student/:id', component: UpdateStudentComponent },
  { path: 'addstudent', component: AddstudentComponent },
  { path: 'uploadstudent', component: UploadStudentsComponent },
  { path: 'site', component: SiteComponent },
  { path: 'promotionlist', component: PromotionComponent },
  { path: 'groupelist', component: GroupeComponent },
  { path: 'addgroup', component: AddGroupComponent },
  { path: 'updategroup/:id', component: UpdateGroupComponent },
  { path: 'scorestudent', component: ScoreStudentComponent },
  { path: 'addpromo', component: AddPromoComponent },
  { path: 'updatepromo/:id', component: UpdatePromoComponent },
  { path: 'addsite', component: AddSiteComponent },
  { path: 'score', component: ScoreComponent },
  { path: 'semestre', component: SemestreComponent },
  { path: 'addsemestre', component: AddSemestreComponent },
  { path: 'updatesemestre/:id', component: UpdateSemestreComponent },

  // Redirection finale
  { path: '**', redirectTo: '' }
];