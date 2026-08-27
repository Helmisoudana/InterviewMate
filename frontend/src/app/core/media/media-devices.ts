import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class MediaDeviceService {
  private activeStream: MediaStream | null = null;

  async getMediaStream(
    constraints: MediaStreamConstraints = {
      video: true,
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 16000,
      },
    }
  ): Promise<MediaStream> {
    try {
      this.activeStream = await navigator.mediaDevices.getUserMedia(constraints);
      return this.activeStream;
    } catch (error) {
      console.error('Erreur lors de la récupération du flux média :', error);
      throw error;
    }
  }

  toggleVideoTrack(enabled: boolean): void {
    if (this.activeStream) {
      this.activeStream.getVideoTracks().forEach((track) => (track.enabled = enabled));
    }
  }

  toggleAudioTrack(enabled: boolean): void {
    if (this.activeStream) {
      this.activeStream.getAudioTracks().forEach((track) => (track.enabled = enabled));
    }
  }

  stopAllTracks(): void {
    if (this.activeStream) {
      this.activeStream.getTracks().forEach((track) => track.stop());
      this.activeStream = null;
    }
  }

  getCurrentStream(): MediaStream | null {
    return this.activeStream;
  }
}