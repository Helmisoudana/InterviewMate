import { Injectable, signal, computed, OnDestroy, inject } from '@angular/core';
import { InterviewRoomState, InterviewPhase, TranscriptMessage } from './interview-room.models';
import { GatewaySocket } from '../../core/gateway/gateway-socket';
import { MediaDeviceService } from '../../core/media/media-devices';
import { InterviewConfig } from '../../core/gateway/gateway.types';

const INITIAL_STATE: InterviewRoomState = {
  phase: 'intro',
  callDurationSeconds: 0,
  isMuted: false,
  isVideoOn: true,
  isCallConnected: false,
  agentSpeaking: false,
  candidateSpeaking: false,
  transcript: [],
};

const ASR_TARGET_SAMPLE_RATE = 16000;

export type RoomStatus = 'connecting' | 'preparing' | 'live' | 'error';

@Injectable()
export class InterviewRoomStore implements OnDestroy {
  private readonly gateway = inject(GatewaySocket);
  private readonly mediaDevice = inject(MediaDeviceService);

  private readonly _state = signal<InterviewRoomState>(INITIAL_STATE);

  readonly phase = computed(() => this._state().phase);
  readonly callDurationSeconds = computed(() => this._state().callDurationSeconds);
  readonly isMuted = computed(() => this._state().isMuted);
  readonly isVideoOn = computed(() => this._state().isVideoOn);
  readonly isCallConnected = computed(() => this._state().isCallConnected);
  readonly agentSpeaking = computed(() => this._state().agentSpeaking);
  readonly candidateSpeaking = computed(() => this._state().candidateSpeaking);
  readonly transcript = computed(() => this._state().transcript);
  readonly connectionStatus = this.gateway.status;

  readonly roomStatus = signal<RoomStatus>('connecting');
  readonly errorMessage = signal<string | null>(null);

  readonly loadingLabel = computed(() => {
    switch (this.roomStatus()) {
      case 'connecting':
        return 'Connexion en cours…';
      case 'preparing':
        return 'Votre coach IA prépare la première question…';
      default:
        return 'Chargement…';
    }
  });

  readonly formattedDuration = computed(() => {
    const totalSeconds = this.callDurationSeconds();
    const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
    const seconds = (totalSeconds % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  });

  private timerInterval: any = null;

  private audioContext: AudioContext | null = null;
  private micProcessor: ScriptProcessorNode | null = null;
  private micSource: MediaStreamAudioSourceNode | null = null;

  private playbackContext: AudioContext | null = null;
  private playbackQueueTime = 0;

  toggleMute(): void {
    this._state.update((s) => {
      const newMuted = !s.isMuted;
      console.log(`[InterviewRoomStore] Micro Mute togglé: ${newMuted}`);
      return { ...s, isMuted: newMuted };
    });
  }

  toggleVideo(): void {
    this._state.update((s) => ({ ...s, isVideoOn: !s.isVideoOn }));
  }

  async startSession(sessionId: string, config: InterviewConfig): Promise<void> {
    if (this._state().isCallConnected) return;

    console.log('[InterviewRoomStore] Démarrage de la session avec config:', config);
    this.roomStatus.set('connecting');
    this.errorMessage.set(null);

    this.gateway.connect(sessionId, config, false, {
      onSessionReady: () => this.handleSessionReady(),
      onAgentMessage: (text) => this.handleAgentMessage(text),
      onTranscription: (text) => this.handleTranscription(text),
      onAgentSpeakingStateChange: (isSpeaking) => {
        console.log(`[InterviewRoomStore] Signal Réseau AgentSpeaking: ${isSpeaking}`);
        this.setAgentSpeaking(isSpeaking);
      },
      onAudioChunk: (chunk) => this.enqueueAudioPlayback(chunk),
      onClose: (code, reason) => this.handleClose(code, reason),
      onError: (e) => console.error('[InterviewRoomStore] Erreur WebSocket', e),
    });
  }

  private handleSessionReady(): void {
    console.log('[InterviewRoomStore] Session Prête (Session Ready)');
    this._state.update((s) => ({ ...s, isCallConnected: true }));
    this.roomStatus.set('preparing');

    this.timerInterval = setInterval(() => {
      this._state.update((s) => ({ ...s, callDurationSeconds: s.callDurationSeconds + 1 }));
    }, 1000);

    this.startMicStreaming();
  }

  private handleAgentMessage(text: string): void {
    console.log('[InterviewRoomStore] Message Agent reçu:', text);
    this.setAgentSpeaking(true);
    this.addMessage('agent', text);
  }

  private handleTranscription(text: string): void {
    console.log('[InterviewRoomStore] Transcription Candidat reçue:', text);
    this.setCandidateSpeaking(false);
    this.addMessage('candidate', text);
  }

  private handleClose(code: number, reason: string): void {
    console.warn(`[InterviewRoomStore] Session fermée (${code}) : ${reason}`);
    if (this.roomStatus() !== 'live') {
      this.roomStatus.set('error');
      this.errorMessage.set(reason);
    }
    this.endCall();
  }

  endCall(): void {
    console.log('[InterviewRoomStore] Fin de l\'appel');
    if (this.timerInterval) clearInterval(this.timerInterval);
    this.stopMicStreaming();
    this.stopPlaybackAudio();
    this.gateway.close();

    this._state.update((s) => ({
      ...s,
      isCallConnected: false,
      phase: 'completed',
      agentSpeaking: false,
      candidateSpeaking: false,
    }));
  }

  private startMicStreaming(): void {
    const stream = this.mediaDevice.getCurrentStream();
    if (!stream) {
      console.error('[InterviewRoomStore] Aucun flux micro disponible.');
      return;
    }

    console.log('[InterviewRoomStore] Initialisation du streaming Micro...');
    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
    this.audioContext = new AudioCtx();

    this.micSource = this.audioContext.createMediaStreamSource(stream);
    this.micProcessor = this.audioContext.createScriptProcessor(4096, 1, 1);

    const inputSampleRate = this.audioContext.sampleRate;

    this.micProcessor.onaudioprocess = (event: AudioProcessingEvent) => {
      const isMuted = this._state().isMuted;
      const isConnected = this._state().isCallConnected;
      const isAgentSpeaking = this._state().agentSpeaking;

      if (isMuted || !isConnected || isAgentSpeaking) {
        if (this._state().candidateSpeaking) {
          this.setCandidateSpeaking(false);
        }
        return; // ON N'ENVOIE RIEN AU BACKEND
      }

      const input = event.inputBuffer.getChannelData(0);
      const pcm16 = this.downsampleAndEncodePCM16(input, inputSampleRate, ASR_TARGET_SAMPLE_RATE);

      this.gateway.sendAudioChunk(pcm16.buffer as ArrayBuffer);

      const rms = Math.sqrt(input.reduce((sum, v) => sum + v * v, 0) / input.length);
      this.setCandidateSpeaking(rms > 0.02);
    };

    this.micSource.connect(this.micProcessor);
    this.micProcessor.connect(this.audioContext.destination);
  }

  private stopMicStreaming(): void {
    console.log('[InterviewRoomStore] Arrêt du streaming Micro');
    this.micProcessor?.disconnect();
    this.micSource?.disconnect();
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
    }
    this.micProcessor = null;
    this.micSource = null;
    this.audioContext = null;
  }

  private stopPlaybackAudio(): void {
    if (this.playbackContext && this.playbackContext.state !== 'closed') {
      this.playbackContext.close();
    }
    this.playbackContext = null;
    this.playbackQueueTime = 0;
  }

  private downsampleAndEncodePCM16(
    input: Float32Array,
    inputSampleRate: number,
    targetSampleRate: number,
  ): Int16Array {
    if (targetSampleRate === inputSampleRate) {
      return this.floatTo16BitPCM(input);
    }
    const ratio = inputSampleRate / targetSampleRate;
    const newLength = Math.round(input.length / ratio);
    const result = new Float32Array(newLength);
    for (let i = 0; i < newLength; i++) {
      result[i] = input[Math.floor(i * ratio)];
    }
    return this.floatTo16BitPCM(result);
  }

  private floatTo16BitPCM(input: Float32Array): Int16Array {
    const output = new Int16Array(input.length);
    for (let i = 0; i < input.length; i++) {
      const s = Math.max(-1, Math.min(1, input[i]));
      output[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }
    return output;
  }

  private readonly TTS_FALLBACK_SAMPLE_RATE = 16000;

  private async enqueueAudioPlayback(chunk: ArrayBuffer): Promise<void> {
    if (!this._state().isCallConnected) return;

    if (!this.playbackContext) {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      this.playbackContext = new AudioCtx({ sampleRate: 16000 });
      this.playbackQueueTime = this.playbackContext.currentTime;
    }

    if (this.playbackContext.state === 'suspended') {
      await this.playbackContext.resume();
    }

    let audioBuffer: AudioBuffer;
    try {
      audioBuffer = await this.playbackContext.decodeAudioData(chunk.slice(0));
    } catch {
      audioBuffer = this.decodeRawPCM16(chunk, this.TTS_FALLBACK_SAMPLE_RATE);
    }

    const source = this.playbackContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(this.playbackContext.destination);

    const startAt = Math.max(this.playbackContext.currentTime, this.playbackQueueTime);
    source.start(startAt);
    this.playbackQueueTime = startAt + audioBuffer.duration;

    if (this.roomStatus() !== 'live') {
      this.roomStatus.set('live');
    }

    // Activer l'état AgentSpeaking pour verrouiller le micro
    this.setAgentSpeaking(true);

    source.onended = () => {
      // Vérification que tous les chunks audio enregistrés ont fini de jouer
      if (this.playbackContext && this.playbackContext.currentTime >= this.playbackQueueTime - 0.05) {
        console.log('[InterviewRoomStore] 🔊 L\'Agent a fini de parler. Libération du micro candidat.');
        this.setAgentSpeaking(false);
      }
    };
  }

  private decodeRawPCM16(chunk: ArrayBuffer, sampleRate: number): AudioBuffer {
    const int16 = new Int16Array(chunk);
    const float32 = new Float32Array(int16.length);
    for (let i = 0; i < int16.length; i++) {
      float32[i] = int16[i] / 32768;
    }
    const buffer = this.playbackContext!.createBuffer(1, float32.length, sampleRate);
    buffer.copyToChannel(float32, 0);
    return buffer;
  }

  private setAgentSpeaking(speaking: boolean): void {
    if (this._state().agentSpeaking !== speaking) {
      console.log(`[InterviewRoomStore] State agentSpeaking changé à : ${speaking} ${speaking ? '⛔ (Audio candidat bloqué)' : '🎙️ (Micro candidat ouvert)'}`);
      this._state.update((s) => ({ ...s, agentSpeaking: speaking }));
    }
  }

  private setCandidateSpeaking(speaking: boolean): void {
    if (this._state().candidateSpeaking !== speaking) {
      this._state.update((s) => ({ ...s, candidateSpeaking: speaking }));
    }
  }

  private addMessage(sender: 'agent' | 'candidate', text: string): void {
    const newMessage: TranscriptMessage = {
      id: Date.now().toString(),
      sender,
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    this._state.update((s) => ({ ...s, transcript: [...s.transcript, newMessage] }));
  }

  ngOnDestroy(): void {
    this.endCall();
  }
}