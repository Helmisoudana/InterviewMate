import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-control-bar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './control-bar.html',
  styleUrl: './control-bar.scss',
})
export class ControlBar {
  readonly isMuted = input<boolean>(false);
  readonly isVideoOn = input<boolean>(true);
  readonly showTranscript = input<boolean>(false);
  readonly duration = input<string>('00:00');

  readonly toggleMute = output<void>();
  readonly toggleVideo = output<void>();
  readonly toggleTranscript = output<void>();
  readonly endCall = output<void>();
}