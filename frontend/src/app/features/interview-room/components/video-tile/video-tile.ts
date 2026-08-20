import {
  Component,
  ElementRef,
  OnInit,
  OnDestroy,
  ViewChild,
  input,
  inject,
  effect,
  signal,
  AfterViewInit,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MediaDeviceService } from '../../../../core/media/media-devices';
import { AudioStreamService } from '../../../../core/media/audio-stream';

@Component({
  selector: 'app-video-tile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './video-tile.html',
  styleUrl: './video-tile.scss',
})
export class VideoTile implements OnInit, AfterViewInit, OnDestroy {
  private readonly mediaDevice = inject(MediaDeviceService);
  private readonly audioStream = inject(AudioStreamService);

  @ViewChild('userVideo') videoElement?: ElementRef<HTMLVideoElement>;

  readonly isVideoOn = input<boolean>(true);
  readonly isMuted = input<boolean>(false);
  readonly isSpeaking = input<boolean>(false);

  readonly audioLevel = signal<number>(0);
  private animId?: number;

  constructor() {
    effect(() => {
      this.mediaDevice.toggleVideoTrack(this.isVideoOn());
      if (this.isVideoOn()) {
        setTimeout(() => this.attachVideoStream(), 0);
      }
    });

    effect(() => {
      this.mediaDevice.toggleAudioTrack(!this.isMuted());
    });
  }

  async ngOnInit(): Promise<void> {
    try {
      let stream = this.mediaDevice.getCurrentStream();
      if (!stream) {
        stream = await this.mediaDevice.getMediaStream({ video: true, audio: true });
      }

      this.audioStream.attachStream(stream);
      this.listenAudioVolume();
    } catch (err) {
      console.error('Erreur accès caméra/micro :', err);
    }
  }

  ngAfterViewInit(): void {
    this.attachVideoStream();
  }

  private attachVideoStream(): void {
    const stream = this.mediaDevice.getCurrentStream();
    if (stream && this.videoElement?.nativeElement) {
      this.videoElement.nativeElement.srcObject = stream;
      this.videoElement.nativeElement.play().catch(() => {});
    }
  }

  private listenAudioVolume(): void {
    const update = () => {
      if (!this.isMuted()) {
        const level = this.audioStream.getVolumeLevel();
        this.audioLevel.set(level);
      } else {
        this.audioLevel.set(0);
      }
      this.animId = requestAnimationFrame(update);
    };
    update();
  }

  ngOnDestroy(): void {
    if (this.animId) cancelAnimationFrame(this.animId);
    this.audioStream.stop();
    this.mediaDevice.stopAllTracks();
  }
}