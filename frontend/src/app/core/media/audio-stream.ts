import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class AudioStreamService {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphoneSource: MediaStreamAudioSourceNode | null = null;
  private highPassFilter: BiquadFilterNode | null = null;
  private lowPassFilter: BiquadFilterNode | null = null;
  private compressor: DynamicsCompressorNode | null = null;
  private gateGainNode: GainNode | null = null;
  private dataArray: Uint8Array<ArrayBuffer> | null = null;

  private readonly NOISE_GATE_THRESHOLD = 12;

  attachStream(stream: MediaStream): void {
    this.stop();

    const AudioCtx =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    this.audioContext = new AudioCtx();

    this.microphoneSource = this.audioContext.createMediaStreamSource(stream);

    this.highPassFilter = this.audioContext.createBiquadFilter();
    this.highPassFilter.type = 'highpass';
    this.highPassFilter.frequency.setValueAtTime(100, this.audioContext.currentTime);

    this.lowPassFilter = this.audioContext.createBiquadFilter();
    this.lowPassFilter.type = 'lowpass';
    this.lowPassFilter.frequency.setValueAtTime(3400, this.audioContext.currentTime);

    this.compressor = this.audioContext.createDynamicsCompressor();
    this.compressor.threshold.setValueAtTime(-24, this.audioContext.currentTime);
    this.compressor.knee.setValueAtTime(30, this.audioContext.currentTime);
    this.compressor.ratio.setValueAtTime(12, this.audioContext.currentTime);
    this.compressor.attack.setValueAtTime(0.003, this.audioContext.currentTime);
    this.compressor.release.setValueAtTime(0.25, this.audioContext.currentTime);

    this.gateGainNode = this.audioContext.createGain();

    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 64;

    this.microphoneSource
      .connect(this.highPassFilter)
      .connect(this.lowPassFilter)
      .connect(this.compressor)
      .connect(this.gateGainNode)
      .connect(this.analyser);

    this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
  }

  getVolumeLevel(): number {
    if (!this.analyser || !this.dataArray || !this.gateGainNode || !this.audioContext) {
      return 0;
    }

    this.analyser.getByteFrequencyData(this.dataArray);

    const sum = this.dataArray.reduce((acc, val) => acc + val, 0);
    const average = sum / this.dataArray.length;
    const rawVolume = Math.round((average / 128) * 100);

    const now = this.audioContext.currentTime;
    if (rawVolume < this.NOISE_GATE_THRESHOLD) {
      this.gateGainNode.gain.setTargetAtTime(0, now, 0.05);
      return 0;
    } else {
      this.gateGainNode.gain.setTargetAtTime(1, now, 0.02);
      return Math.min(100, rawVolume);
    }
  }

  stop(): void {
    if (this.microphoneSource) {
      this.microphoneSource.disconnect();
      this.microphoneSource = null;
    }

    if (this.highPassFilter) {
      this.highPassFilter.disconnect();
      this.highPassFilter = null;
    }

    if (this.lowPassFilter) {
      this.lowPassFilter.disconnect();
      this.lowPassFilter = null;
    }

    if (this.compressor) {
      this.compressor.disconnect();
      this.compressor = null;
    }

    if (this.gateGainNode) {
      this.gateGainNode.disconnect();
      this.gateGainNode = null;
    }

    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.analyser = null;
    this.dataArray = null;
  }
}