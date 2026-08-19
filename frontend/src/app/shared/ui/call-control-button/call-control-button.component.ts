import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Bouton rond façon "barre d'appel" (mic / caméra / raccrocher).
 * - variant 'default' : bascule actif/inactif (bleu clair quand actif)
 * - variant 'danger'  : bouton rouge fixe (ex: terminer l'appel)
 *
 * Usage :
 * <app-call-control-button [active]="micEnabled()" (toggle)="toggleMic()">
 *   🎤
 * </app-call-control-button>
 *
 * <app-call-control-button variant="danger" (toggle)="endCall()">
 *   ⏹
 * </app-call-control-button>
 */
@Component({
  selector: 'app-call-control-button',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './call-control-button.component.html',
  styleUrl: './call-control-button.component.scss',
})
export class CallControlButtonComponent {
  @Input() active = true;
  @Input() variant: 'default' | 'danger' = 'default';
  @Input() ariaLabel = 'Contrôle d’appel';
  @Output() toggle = new EventEmitter<void>();

  onClick(): void {
    this.toggle.emit();
  }
}
