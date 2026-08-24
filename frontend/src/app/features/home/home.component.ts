import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

// Composants Partagés
import { AvatarComponent } from '../../shared/ui/avatar/avatar.component';

// Services et Modèles API (Dossier core/api)
import { SessionApi } from '../../core/api/session-api';
import { EntretienBackend } from '../../core/api/model';

export interface HistoryPreviewItem {
  id: string;
  role: string;
  date: string;
  score: string
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink, AvatarComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit {
  private readonly sessionApi = inject(SessionApi);

  readonly recentInterviews = signal<HistoryPreviewItem[]>([]);

  ngOnInit(): void {
    this.chargerEntretiensRecents();
  }

  private chargerEntretiensRecents(): void {
    this.sessionApi.getRecentInterviews(3).subscribe({
      next: (donnees: EntretienBackend[]) => {
        const entretiensFormates: HistoryPreviewItem[] = donnees.map((item) => ({
          id: item.session_id || item.id,
          role: item.poste || 'Poste non spécifié',
          date: this.formaterDate(item.timestamp),
          score: item.statut , 
        }));

        this.recentInterviews.set(entretiensFormates);
      },
      error: (err) => {
        console.error('Erreur lors de la récupération des entretiens :', err);
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
}