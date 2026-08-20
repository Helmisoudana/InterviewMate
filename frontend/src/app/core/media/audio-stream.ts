import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class AudioStreamService {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphoneSource: MediaStreamAudioSourceNode | null = null;
  private dataArray: Uint8Array<ArrayBuffer> | null = null;

  /**
   * Connecte un MediaStream à l'analyseur Audio
   */
  attachStream(stream: MediaStream): void {
    this.stop(); // Nettoie une éventuelle session précédente

    // Création du contexte audio
    const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    this.audioContext = new AudioCtx();

    // Analyseur pour capter la fréquence / l'amplitude
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 64;

    // Connexion du flux micro vers l'analyseur
    this.microphoneSource = this.audioContext.createMediaStreamSource(stream);
    this.microphoneSource.connect(this.analyser);

    this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
  }

  /**
   * Calcule et retourne le niveau de volume actuel (valeur entre 0 et 100)
   */
  getVolumeLevel(): number {
    if (!this.analyser || !this.dataArray) {
      return 0;
    }

    this.analyser.getByteFrequencyData(this.dataArray);
    
    // Moyenne des fréquences captées
    const sum = this.dataArray.reduce((acc, val) => acc + val, 0);
    const average = sum / this.dataArray.length;

    // Normalisation approximative entre 0 et 100
    const volume = Math.round((average / 128) * 100);
    return Math.min(100, volume);
  }

  /**
   * Arrête et ferme proprement le contexte audio
   */
  stop(): void {
    if (this.microphoneSource) {
      this.microphoneSource.disconnect();
      this.microphoneSource = null;
    }

    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.analyser = null;
    this.dataArray = null;
  }
}