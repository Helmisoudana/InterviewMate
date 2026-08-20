import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InterviewPhase } from '../../interview-room.models';

@Component({
  selector: 'app-phase-indicator',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './phase-indicator.html',
  styleUrl: './phase-indicator.scss',
})
export class PhaseIndicator {
  readonly currentPhase = input.required<InterviewPhase>();

  readonly phases: { key: InterviewPhase; label: string }[] = [
    { key: 'intro', label: 'Introduction' },
    { key: 'technical', label: 'Technique' },
    { key: 'situational', label: 'Mise en situation' },
    { key: 'feedback', label: 'Bilan' },
  ];
}