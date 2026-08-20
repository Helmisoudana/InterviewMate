import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-interview-end',
  standalone: true,
  templateUrl: './interview-end.html',
  styleUrl: './interview-end.scss',
})
export class InterviewEndComponent implements OnInit, OnDestroy {
  private readonly router = inject(Router);

  countdown = 60;
  private timerInterval?: number;

  ngOnInit(): void {
    // Compte à rebours avant redirection automatique vers l'accueil
    this.timerInterval = window.setInterval(() => {
      this.countdown--;
      if (this.countdown <= 0) {
        this.goToHome();
      }
    }, 1000);
  }

  ngOnDestroy(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  }

  rejoinInterview(): void {
    this.router.navigate(['/interview']);
  }

  goToHome(): void {
    this.router.navigate(['/']);
  }

  viewReport(): void {
    this.router.navigate(['/report']);
  }

  sendFeedback(): void {
    // Logique pour ouvrir un modal ou formulaire de feedback
  }
}