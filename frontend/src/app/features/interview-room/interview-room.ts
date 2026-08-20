import { Component, inject, OnInit, HostListener, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router'; // 1. Import du Router
import { InterviewRoomStore } from './interview-room.store';
import { PhaseIndicator } from './components/phase-indicator/phase-indicator';
import { AgentTile } from './components/agent-tile/agent-tile';
import { VideoTile } from './components/video-tile/video-tile';
import { LiveTranscript } from './components/live-transcript/live-transcript';
import { ControlBar } from './components/control-bar/control-bar';

@Component({
  selector: 'app-interview-room',
  standalone: true,
  providers: [InterviewRoomStore],
  imports: [
    CommonModule,
    PhaseIndicator,
    AgentTile,
    VideoTile,
    LiveTranscript,
    ControlBar,
  ],
  templateUrl: './interview-room.html',
  styleUrl: './interview-room.scss',
})
export class InterviewRoomComponent implements OnInit {
  readonly store = inject(InterviewRoomStore);
  private readonly router = inject(Router); // 2. Injection du Router

  @ViewChild('mainTile') mainTileRef!: ElementRef<HTMLDivElement>;

  showTranscript = false;

  // Logique Drag & Drop bridé
  isDragging = false;
  pipPosition = { x: 0, y: 0 };
  dragStartPos = { x: 0, y: 0 };

  get pipTransform(): string {
    return `translate3d(${this.pipPosition.x}px, ${this.pipPosition.y}px, 0px)`;
  }

  ngOnInit(): void {
    this.store.startSession();
  }

  toggleTranscript(): void {
    this.showTranscript = !this.showTranscript;
  }

  // 3. Gestion de la fin d'appel et redirection
  onEndCall(): void {
    this.store.endCall();
    this.router.navigate(['/interview/end']);
  }

  // --- Gestion du Drag & Drop avec limites (Bounding Box) ---
  onMouseDown(event: MouseEvent): void {
    this.isDragging = true;
    this.dragStartPos = {
      x: event.clientX - this.pipPosition.x,
      y: event.clientY - this.pipPosition.y,
    };
  }

  @HostListener('document:mousemove', ['$event'])
  onMouseMove(event: MouseEvent): void {
    if (!this.isDragging || !this.mainTileRef) return;

    const mainRect = this.mainTileRef.nativeElement.getBoundingClientRect();
    const pipWidth = 220;  // Largeur de la vignette
    const pipHeight = 135; // Hauteur de la vignette
    const padding = 16;    // Marge intérieure (padding)

    // Calcul de la nouvelle position théorique
    let newX = event.clientX - this.dragStartPos.x;
    let newY = event.clientY - this.dragStartPos.y;

    // Calcul des limites maximales et minimales de déplacement
    const minX = -(mainRect.width - pipWidth - padding * 2);
    const maxX = 0;
    const minY = -(mainRect.height - pipHeight - padding * 2);
    const maxY = 0;

    // Blocage (Clamping) des coordonnées pour ne pas dépasser
    this.pipPosition = {
      x: Math.min(Math.max(newX, minX), maxX),
      y: Math.min(Math.max(newY, minY), maxY),
    };
  }

  @HostListener('document:mouseup')
  onMouseUp(): void {
    this.isDragging = false;
  }
}