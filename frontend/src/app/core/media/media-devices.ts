import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class MediaDeviceService {
  private activeStream: MediaStream | null = null;

  /**
   * Demande l'accès à la caméra et/ou au microphone
   */
  async getMediaStream(constraints: MediaStreamConstraints = { video: true, audio: true }): Promise<MediaStream> {
    try {
      this.activeStream = await navigator.mediaDevices.getUserMedia(constraints);
      return this.activeStream;
    } catch (error) {
      console.error('Erreur lors de la récupération du flux média :', error);
      throw error;
    }
  }

  /**
   * Active ou désactive les pistes vidéo
   */
  toggleVideoTrack(enabled: boolean): void {
    if (this.activeStream) {
      this.activeStream.getVideoTracks().forEach((track) => (track.enabled = enabled));
    }
  }

  /**
   * Active ou désactive les pistes audio
   */
  toggleAudioTrack(enabled: boolean): void {
    if (this.activeStream) {
      this.activeStream.getAudioTracks().forEach((track) => (track.enabled = enabled));
    }
  }

  /**
   * Arrête proprement toutes les pistes (libère la caméra/micro)
   */
  stopAllTracks(): void {
    if (this.activeStream) {
      this.activeStream.getTracks().forEach((track) => track.stop());
      this.activeStream = null;
    }
  }

  /**
   * Retourne le flux actuellement actif
   */
  getCurrentStream(): MediaStream | null {
    return this.activeStream;
  }
}