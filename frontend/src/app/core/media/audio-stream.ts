import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class AudioStreamService {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphoneSource: MediaStreamAudioSourceNode | null = null;
  private filterNode: BiquadFilterNode | null = null; // Filtre anti-bruit
  private dataArray: Uint8Array<ArrayBuffer> | null = null;

  attachStream(stream: MediaStream): void {
    this.stop(); 

    const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    this.audioContext = new AudioCtx();

    // 1. Création de l'Analyser pour le niveau sonore
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 64;

    // 2. Création du Filtre Passe-Haut (High-Pass Filter) pour éliminer le bruit de fond
    this.filterNode = this.audioContext.createBiquadFilter();
    this.filterNode.type = 'highpass';
    this.filterNode.frequency.setValueAtTime(85, this.audioContext.currentTime); // Coupe sous 85Hz (bruits parasites)

    // 3. Connexion de la chaîne audio : Source -> Filtre -> Analyser
    this.microphoneSource = this.audioContext.createMediaStreamSource(stream);
    this.microphoneSource.connect(this.filterNode);
    this.filterNode.connect(this.analyser);

    this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
  }

  getVolumeLevel(): number {
    if (!this.analyser || !this.dataArray) {
      return 0;
    }

    this.analyser.getByteFrequencyData(this.dataArray);
    
    const sum = this.dataArray.reduce((acc, val) => acc + val, 0);
    const average = sum / this.dataArray.length;

    const volume = Math.round((average / 128) * 100);
    return Math.min(100, volume);
  }

  stop(): void {
    if (this.microphoneSource) {
      this.microphoneSource.disconnect();
      this.microphoneSource = null;
    }

    if (this.filterNode) {
      this.filterNode.disconnect();
      this.filterNode = null;
    }

    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.analyser = null;
    this.dataArray = null;
  }
}