import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

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
  score: number;
  messages: ChatMessage[];
}

@Component({
  selector: 'app-interview-history',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './interview-history.html',
  styleUrl: './interview-history.scss',
})
export class InterviewHistoryComponent {
  // Liste d'exemples d'entretiens enregistrés
  sessions = signal<InterviewSession[]>([
    {
      id: '1',
      title: 'Développeur Frontend Angular',
      date: '19 août 2026',
      duration: '15 min 42 sec',
      score: 85,
      messages: [
        { sender: 'ai', text: 'Bonjour ! Bienvenue à votre entretien pour le poste de Développeur Frontend Angular. Pouvez-vous vous présenter ?', time: '10:00' },
        { sender: 'user', text: 'Bonjour ! Je suis développeur depuis 3 ans avec une spécialisation sur Angular et TypeScript.', time: '10:01' },
        { sender: 'ai', text: 'Très bien. Pouvez-vous m\'expliquer la différence entre un Signal et un BehaviorSubject dans Angular ?', time: '10:02' },
        { sender: 'user', text: 'Les Signals offrent une réactivité fine sans avoir besoin de souscrire explicitement, contrairement aux Observables/BehaviorSubject.', time: '10:04' },
        { sender: 'ai', text: 'Excellente réponse ! Merci pour cet entretien, nous avons terminé.', time: '10:15' }
      ]
    },
    {
      id: '2',
      title: 'Développeur Fullstack Node/Angular',
      date: '12 août 2026',
      duration: '22 min 10 sec',
      score: 78,
      messages: [
        { sender: 'ai', text: 'Bonjour, prêt à commencer l\'évaluation Fullstack ?', time: '14:30' },
        { sender: 'user', text: 'Tout à fait, je suis prêt !', time: '14:31' },
        { sender: 'ai', text: 'Parfait. Comment gérez-vous les transactions dans PostgreSQL avec Node.js ?', time: '14:32' }
      ]
    }
  ]);

  // Session sélectionnée par défaut (la première)
  selectedSession = signal<InterviewSession | null>(this.sessions()[0]);

  selectSession(session: InterviewSession): void {
    this.selectedSession.set(session);
  }
}