import { Component, Input, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

export type BadgeStatus = 'connected' | 'connecting' | 'reconnecting' | 'ended' | 'error';

@Component({
  selector: 'app-badge-status',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './badge-status.component.html',
  styleUrl: './badge-status.component.scss',
})
export class BadgeStatusComponent {
  private readonly _status = signal<BadgeStatus>('connecting');

  @Input() set status(value: BadgeStatus) {
    this._status.set(value);
  }
  get status(): BadgeStatus {
    return this._status();
  }

  @Input() label?: string;

  readonly displayLabel = computed(() => this.label ?? this.defaultLabel());

  private defaultLabel(): string {
    switch (this._status()) {
      case 'connected':
        return 'Connecté';
      case 'connecting':
        return 'Connexion…';
      case 'reconnecting':
        return 'Reconnexion…';
      case 'ended':
        return 'Terminé';
      case 'error':
        return 'Erreur';
    }
  }
}
