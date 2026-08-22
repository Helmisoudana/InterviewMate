import { Component, ElementRef, OnInit, OnDestroy, ViewChild, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MediaDeviceService } from '../../core/media/media-devices';
import { AudioStreamService } from '../../core/media/audio-stream';
import { InterviewConfig } from '../../core/gateway/gateway.types';

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

  private routerState: { sessionId?: string; config?: InterviewConfig } = {};

  async ngOnInit(): Promise<void> {
    this.routerState = history.state as { sessionId?: string; config?: InterviewConfig };

    if (!this.routerState?.sessionId || !this.routerState?.config) {
      console.error('[PreCallComponent] session_id/config manquants — retour à la configuration.');
      this.router.navigate(['/setup']);
      return;
    }

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

  joinInterview(): void {
    this.router.navigate(['/interview'], { state: this.routerState });
  }

  ngOnDestroy(): void {
    if (this.animId) cancelAnimationFrame(this.animId);
    this.audioStream.stop();
  }
}