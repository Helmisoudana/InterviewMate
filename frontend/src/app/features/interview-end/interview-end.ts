import { Component, inject, OnInit, OnDestroy, signal } from '@angular/core';
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

  sessionId = '';
  isDownloading = signal(false);

  ngOnInit(): void {
    const state = history.state as { sessionId?: string };
    if (state?.sessionId) {
      this.sessionId = state.sessionId;
    }

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
    this.router.navigate(['/setup']);
  }

  goToHome(): void {
    this.router.navigate(['/home']);
  }

  async viewReport(): Promise<void> {
    if (!this.sessionId) {
      this.goToHome();
      return;
    }

    this.isDownloading.set(true);

    try {
      const response = await fetch(`http://127.0.0.1:8000/scoring/${this.sessionId}/pdf`);
      
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rapport_${this.sessionId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      this.goToHome();
    } catch (error) {
      console.error('[InterviewEndComponent] Erreur lors du téléchargement:', error);
      this.isDownloading.set(false);
      this.goToHome();
    }
  }

  sendFeedback(): void {}
}