import { Component, Input, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-avatar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './avatar.component.html',
  styleUrl: './avatar.component.scss',
})
export class AvatarComponent {
  private readonly _name = signal('?');

  @Input() set name(value: string) {
    this._name.set(value || '?');
  }

  @Input() imageUrl?: string;
  @Input() size: 'sm' | 'md' | 'lg' = 'md';

  /** Utilisé aussi pour l'agent IA pendant l'entretien (variant sans photo, halo bleu clair) */
  @Input() variant: 'user' | 'agent' = 'user';

  readonly initials = computed(() => {
    const parts = this._name().trim().split(' ').filter(Boolean);
    if (parts.length === 0) return '?';
    if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
  });
}
