import { Component, inject, OnInit, HostListener, ViewChild, ElementRef, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { InterviewRoomStore } from './interview-room.store';
import { PhaseIndicator } from './components/phase-indicator/phase-indicator';
import { AgentTile } from './components/agent-tile/agent-tile';
import { VideoTile } from './components/video-tile/video-tile';
import { LiveTranscript } from './components/live-transcript/live-transcript';
import { ControlBar } from './components/control-bar/control-bar';
import { InterviewConfig } from '../../core/gateway/gateway.types';

@Component({
  selector: 'app-interview-room',
  standalone: true,
  providers: [InterviewRoomStore],
  imports: [CommonModule, PhaseIndicator, AgentTile, VideoTile, LiveTranscript, ControlBar],
  templateUrl: './interview-room.html',
  styleUrl: './interview-room.scss',
})
export class InterviewRoomComponent implements OnInit {
  readonly store = inject(InterviewRoomStore);
  private readonly router = inject(Router);

  @ViewChild('mainTile') mainTileRef!: ElementRef<HTMLDivElement>;

  showTranscript = false;
  isDragging = false;
  pipPosition = { x: 0, y: 0 };
  dragStartPos = { x: 0, y: 0 };

  // État de génération du rapport
  isGeneratingReport = signal(false);
  private sessionId = '';

  get pipTransform(): string {
    return `translate3d(${this.pipPosition.x}px, ${this.pipPosition.y}px, 0px)`;
  }

  ngOnInit(): void {
    const state = history.state as { sessionId?: string; config?: InterviewConfig };

    if (!state?.sessionId || !state?.config) {
      console.error('[InterviewRoomComponent] session_id/config manquants — retour à la configuration.');
      this.router.navigate(['/setup']);
      return;
    }

    this.sessionId = state.sessionId;
    this.store.startSession(state.sessionId, state.config);
  }

  toggleTranscript(): void {
    this.showTranscript = !this.showTranscript;
  }

  async onEndCall(): Promise<void> {
    // 1. Déconnexion WebRTC / Clôture de l'appel
    this.store.endCall();
    
    // 2. Affichage de la page de chargement (style waiting-room)
    this.isGeneratingReport.set(true);

    try {
      // 3. Appel de l'API backend pour générer le rapport
      const response = await fetch(`http://127.0.0.1:8000/scoring/${this.sessionId}`);
      
      if (!response.ok) {
        throw new Error(`Erreur lors de la génération du rapport: ${response.statusText}`);
      }

      const rapport = await response.json();

      this.router.navigate(['/interview/end'], {
      state: { sessionId: this.sessionId }
    });

    } catch (error) {
      console.error('[InterviewRoomComponent] Échec lors de la génération du rapport:', error);
      this.isGeneratingReport.set(false);
    }
  }

  backToSetup(): void {
    this.router.navigate(['/setup']);
  }

  onMouseDown(event: MouseEvent): void {
    this.isDragging = true;
    this.dragStartPos = { x: event.clientX - this.pipPosition.x, y: event.clientY - this.pipPosition.y };
  }

  @HostListener('document:mousemove', ['$event'])
  onMouseMove(event: MouseEvent): void {
    if (!this.isDragging || !this.mainTileRef) return;
    const mainRect = this.mainTileRef.nativeElement.getBoundingClientRect();
    const pipWidth = 220;
    const pipHeight = 135;
    const padding = 16;
    let newX = event.clientX - this.dragStartPos.x;
    let newY = event.clientY - this.dragStartPos.y;
    const minX = -(mainRect.width - pipWidth - padding * 2);
    const maxX = 0;
    const minY = -(mainRect.height - pipHeight - padding * 2);
    const maxY = 0;
    this.pipPosition = { x: Math.min(Math.max(newX, minX), maxX), y: Math.min(Math.max(newY, minY), maxY) };
  }

  @HostListener('document:mouseup')
  onMouseUp(): void {
    this.isDragging = false;
  }
}