import { Component, ElementRef, ViewChild, effect, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-agent-tile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './agent-tile.html',
  styleUrl: './agent-tile.scss',
})
export class AgentTile {
  @ViewChild('idleVideo') idleVideo?: ElementRef<HTMLVideoElement>;
  @ViewChild('talkingVideo') talkingVideo?: ElementRef<HTMLVideoElement>;

  readonly isSpeaking = input<boolean>(false);

  readonly idleSource = 'idle.mp4';
  readonly talkingSource = 'talking.mp4';

  constructor() {
    effect(() => {
      this.isSpeaking();
      this.keepVideosPlaying();
    });
  }

  onVideoLoaded(): void {
    this.keepVideosPlaying();
  }

  private keepVideosPlaying(): void {
    const idle = this.idleVideo?.nativeElement;
    const talking = this.talkingVideo?.nativeElement;

    if (idle && idle.paused) {
      idle.play().catch(() => {});
    }
    if (talking && talking.paused) {
      talking.play().catch(() => {});
    }
  }
}