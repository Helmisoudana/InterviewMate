import { Component, ElementRef, OnInit, OnDestroy, ViewChild, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MediaDeviceService } from '../../core/media/media-devices';
import { AudioStreamService } from '../../core/media/audio-stream';

@Component({
  selector: 'app-pre-call',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pre-call.html',
  styleUrl: './pre-call.scss',
})
export class PreCallComponent implements OnInit, OnDestroy {
  private readonly mediaDevice = inject(MediaDeviceService);
  private readonly audioStream = inject(AudioStreamService);
  private readonly router = inject(Router);

  @ViewChild('videoPreview') videoElement!: ElementRef<HTMLVideoElement>;

  isVideoOn = signal(true);
  isMuted = signal(false);
  audioLevel = signal(0);
  private animId?: number;

  async ngOnInit(): Promise<void> {
    try {
      const stream = await this.mediaDevice.getMediaStream();
      if (this.videoElement?.nativeElement) {
        this.videoElement.nativeElement.srcObject = stream;
      }
      this.audioStream.attachStream(stream);
      this.listenAudio();
    } catch (err) {
      console.error('Erreur accès caméra/micro', err);
    }
  }

  private listenAudio(): void {
    const update = () => {
      this.audioLevel.set(this.isMuted() ? 0 : this.audioStream.getVolumeLevel());
      this.animId = requestAnimationFrame(update);
    };
    update();
  }

  toggleVideo(): void {
    this.isVideoOn.update((v) => !v);
    this.mediaDevice.toggleVideoTrack(this.isVideoOn());
  }

  toggleMute(): void {
    this.isMuted.update((m) => !m);
    this.mediaDevice.toggleAudioTrack(!this.isMuted());
  }

  // --- LIAISON AVEC L'INTERVIEW ROOM ---
  joinInterview(): void {
    // Redirige vers la salle d'entretien
    this.router.navigate(['/interview']);
  }

  ngOnDestroy(): void {
    if (this.animId) cancelAnimationFrame(this.animId);
    this.audioStream.stop();
  }
}