import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import {
  DifficulteEntretien,
  DureeEntretien,
  DIFFICULTE_OPTIONS,
  DUREE_OPTIONS,
  InterviewConfig,
} from '../../core/gateway/gateway.types'; 

@Component({
  selector: 'app-interview-setup',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './interview-setup.html',
  styleUrl: './interview-setup.scss',
})
export class InterviewSetupComponent {
  private router = inject(Router);

  readonly dureeOptions = DUREE_OPTIONS;
  readonly difficulteOptions = DIFFICULTE_OPTIONS;

  poste = signal<string>('');
  langue = signal<string>('fr');
  duree = signal<DureeEntretien>('MOYENNE');
  difficulte = signal<DifficulteEntretien>('MOYEN');

  isSubmitting = signal<boolean>(false);

  readonly languesDisponibles = [
    { code: 'fr', label: 'Français 🇫🇷' },
    { code: 'en', label: 'English 🇬🇧' },
    { code: 'es', label: 'Español 🇪🇸' },
    { code: 'de', label: 'Deutsch 🇩🇪' },
  ];

  selectDuree(value: DureeEntretien): void {
    this.duree.set(value);
  }

  selectDifficulte(value: DifficulteEntretien): void {
    this.difficulte.set(value);
  }

    startInterview(): void {
    if (!this.poste().trim()) {
      return;
    }

    this.isSubmitting.set(true);

    const config: InterviewConfig = {
      poste: this.poste().trim(),
      langue: this.langue(),
      duree: this.duree(),
      difficulte: this.difficulte(),
    };

    const sessionId = crypto.randomUUID();

    this.router.navigate(['/pre-call'], {
      state: { config, sessionId },
    });
  }
}