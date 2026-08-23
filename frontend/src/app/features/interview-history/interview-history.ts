import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

// Service et Modèles API
import { SessionApi } from '../../core/api/session-api';
import { EntretienBackend, EchangeBackend } from '../../core/api/model';

export interface ChatMessage {
  sender: 'ai' | 'user';
  text: string;
  time: string;
}

export interface InterviewSession {
  id: string;
  title: string;
  date: string;
  duration: string;
  score: number | null;
  messages: ChatMessage[];
}

@Component({
  selector: 'app-interview-history',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './interview-history.html',
  styleUrl: './interview-history.scss',
})
export class InterviewHistoryComponent implements OnInit {
  private readonly sessionApi = inject(SessionApi);

  // Signaux pour les états dynamiques
  readonly sessions = signal<InterviewSession[]>([]);
  readonly selectedSession = signal<InterviewSession | null>(null);
  readonly isLoadingMessages = signal<boolean>(false);

  ngOnInit(): void {
    this.chargerSessions();
  }

  /**
   * Charger la liste des entretiens depuis l'API
   */
  private chargerSessions(): void {
    this.sessionApi.getRecentInterviews(20).subscribe({
      next: (data: EntretienBackend[]) => {
        const listeFormatee: InterviewSession[] = data.map((item) => ({
          id: item.session_id || item.id,
          title: item.poste || 'Entretien sans titre',
          date: this.formaterDate(item.timestamp),
          duration: '15 min', // Optionnel ou calculable selon tes colonnes
          score: item.statut === 'EN_COURS' ? null : 80,
          messages: [], // Sera chargé lors de la sélection
        }));

        this.sessions.set(listeFormatee);

        // Sélectionner le premier entretien par défaut s'il y en a
        if (listeFormatee.length > 0) {
          this.selectSession(listeFormatee[0]);
        }
      },
      error: (err) => console.error('Erreur chargement entretiens :', err),
    });
  }

  /**
   * Sélectionner un entretien et charger ses messages/échanges
   */
  selectSession(session: InterviewSession): void {
    this.selectedSession.set(session);
    this.isLoadingMessages.set(true);

    this.sessionApi.getEchangesBySession(session.id).subscribe({
      next: (echanges: EchangeBackend[]) => {
        const messages: ChatMessage[] = [];

        // Transformer chaque ligne d'échange en 2 bulles de chat (Agent -> Candidat)
        echanges.forEach((ech) => {
          if (ech.question_agent) {
            messages.push({
              sender: 'ai',
              text: ech.question_agent,
              time: this.extraireHeure(ech.horodatage),
            });
          }
          if (ech.reponse_candidat) {
            messages.push({
              sender: 'user',
              text: ech.reponse_candidat,
              time: this.extraireHeure(ech.horodatage),
            });
          }
        });

        // Mettre à jour la session sélectionnée avec ses vrais messages
        const updatedSession = { ...session, messages };
        this.selectedSession.set(updatedSession);
        this.isLoadingMessages.set(false);
      },
      error: (err) => {
        console.error('Erreur chargement des échanges :', err);
        this.isLoadingMessages.set(false);
      },
    });
  }

  private formaterDate(isoTimestamp: string): string {
    if (!isoTimestamp) return '';
    const date = new Date(isoTimestamp);
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  }

  private extraireHeure(isoTimestamp?: string): string {
    if (!isoTimestamp) return '';
    const date = new Date(isoTimestamp);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  }
}