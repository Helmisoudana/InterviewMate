import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class AudioStreamService {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphoneSource: MediaStreamAudioSourceNode | null = null;
  private dataArray: Uint8Array<ArrayBuffer> | null = null;

  attachStream(stream: MediaStream): void {
    this.stop(); 

    const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    this.audioContext = new AudioCtx();

    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 64;

    this.microphoneSource = this.audioContext.createMediaStreamSource(stream);
    this.microphoneSource.connect(this.analyser);

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

    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.analyser = null;
    this.dataArray = null;
  }
}