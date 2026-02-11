import { Component, OnInit, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AnimateOnScrollDirective } from '../Directives/animate-on-scroll.directive';
import { NavbarComponent } from '../navbar/navbar.component';
import { FooterComponent } from '../footer/footer.component';
// N'oubliez pas d'importer votre directive si vous travaillez en standalone

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  imports: [CommonModule, FormsModule, RouterModule, AnimateOnScrollDirective, NavbarComponent]
})
export class HomeComponent implements OnInit, AfterViewInit, OnDestroy {
  darkMode = false;
  // Remettre les propriétés liées au carrousel
  private currentSlide = 0;
  private slides: HTMLElement[] = [];
  private interval: any;
  private slideDuration = 6000; // 6 secondes par slide

  services = [
    { title: 'Créer un Test', description: 'Gérez vos tests TOEIC en quelques clics.', icon: 'fas fa-book' },
    { title: 'Gérer les Classes', description: 'Organisez vos groupes d\'étudiants.', icon: 'fas fa-users' },
    { title: 'Suivi des Évaluations', description: 'Analysez la progression des étudiants.', icon: 'fas fa-chart-line' },
    { title: 'Importer les Copies', description: 'Importez et corrigez automatiquement les réponses.', icon: 'fas fa-upload' },
    { title: 'Impression', description: 'Imprimez les feuilles de réponses.', icon: 'fas fa-print' }
  ];

  constructor() { }

  ngOnInit(): void {
  }

  ngAfterViewInit(): void {
    // Remettre l'initialisation du carrousel (avec setTimeout)
    setTimeout(() => {
      console.log('Initializing carousel...');
      this.initCarousel();
      this.startCarousel();
    }, 0);
    this.initScrollAnimationObserver(); 
  }

  ngOnDestroy(): void {
    // Remettre l'arrêt du carrousel
    this.stopCarousel();
    this.disconnectScrollObserver();
  }

  // Remettre les méthodes liées au carrousel
  private initCarousel(): void {
    const carouselContainer = document.querySelector('.hero-carousel') as HTMLElement;
    if (carouselContainer) {
      this.slides = Array.from(carouselContainer.querySelectorAll('.carousel-slide')) as HTMLElement[];
      console.log(`Found ${this.slides.length} slides.`);
      if (this.slides.length > 0) {
        this.slides.forEach(slide => slide.classList.remove('active')); // Assurer qu'aucun n'est actif au début
        this.slides[0].classList.add('active'); 
        console.log('Added active class to first slide:', this.slides[0]);
      } else {
        console.log('No slides found inside .hero-carousel');
      }
    } else {
       console.error('.hero-carousel element not found');
    }
  }

  private startCarousel(): void {
    if (this.slides.length > 1) { 
      console.log(`Starting carousel interval (${this.slideDuration}ms)`);
      this.interval = setInterval(() => {
        this.nextSlide();
      }, this.slideDuration);
    } else {
       console.log('Carousel not started (less than 2 slides)');
    }
  }

  private stopCarousel(): void {
    if (this.interval) {
      console.log('Stopping carousel interval');
      clearInterval(this.interval);
    }
  }

  private nextSlide(): void {
    const nextIndex = (this.currentSlide + 1) % this.slides.length;
    console.log(`Moving to next slide: index ${nextIndex}`);
    this.goToSlide(nextIndex);
  }

  private goToSlide(index: number): void {
    if (index === this.currentSlide || !this.slides[this.currentSlide] || !this.slides[index]) {
        console.warn(`goToSlide(${index}) aborted: same index or slides not found.`);
        return;
    }
    
    console.log(`Removing active class from slide ${this.currentSlide}:`, this.slides[this.currentSlide]);
    this.slides[this.currentSlide].classList.remove('active');
    this.currentSlide = index;
    console.log(`Adding active class to slide ${this.currentSlide}:`, this.slides[this.currentSlide]);
    this.slides[this.currentSlide].classList.add('active');

    // Redémarrer l'intervalle 
    this.stopCarousel();
    this.startCarousel();
  }

  // ---- Animation au défilement (Garder cette partie) ----
  private scrollObserver?: IntersectionObserver;

  private initScrollAnimationObserver(): void {
    const options = {
      root: null, 
      rootMargin: '0px',
      threshold: 0.1 
    };

    this.scrollObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          // observer.unobserve(entry.target);
        } else {
          // entry.target.classList.remove('visible');
        }
      });
    }, options);

    const elementsToAnimate = document.querySelectorAll('.animate-on-scroll');
    elementsToAnimate.forEach(el => {
      if (this.scrollObserver) {
        this.scrollObserver.observe(el);
      }
    });
  }

  private disconnectScrollObserver(): void {
    if (this.scrollObserver) {
      this.scrollObserver.disconnect();
    }
  }

  toggleDarkMode() {
    this.darkMode = !this.darkMode;
    document.body.classList.toggle('dark-mode');
  }
}