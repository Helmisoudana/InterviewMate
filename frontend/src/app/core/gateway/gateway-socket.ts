import { Injectable, signal } from '@angular/core';
import { environment } from '../../../environments/environment';
import {
  GatewayInitMessage,
  GatewayIncomingMessage,
  InterviewConfig,
  GatewayCloseCode,
  GATEWAY_CLOSE_REASONS,
  GatewayConnectionStatus,
} from './gateway.types';

export interface GatewayCallbacks {
  onSessionReady?: () => void;
  onReconnected?: () => void;
  onTranscription?: (text: string) => void;
  onAgentMessage?: (text: string) => void;
  onAgentSpeakingStateChange?: (isSpeaking: boolean) => void;
  onAudioChunk?: (chunk: ArrayBuffer) => void;
  onClose?: (code: number, reason: string) => void;
  onError?: (event: Event) => void;
}

@Injectable({
  providedIn: 'root',
})
export class GatewaySocket {
  private ws: WebSocket | null = null;
  private callbacks: GatewayCallbacks = {};

  readonly status = signal<GatewayConnectionStatus>('idle');

  connect(
    sessionId: string,
    config: InterviewConfig | undefined,
    reconnect: boolean,
    callbacks: GatewayCallbacks,
  ): void {
    this.callbacks = callbacks;
    this.status.set(reconnect ? 'reconnecting' : 'connecting');

    this.ws = new WebSocket(environment.wsUrl);
    this.ws.binaryType = 'arraybuffer';

    this.ws.onopen = () => {
      const initMessage: GatewayInitMessage = reconnect
        ? { session_id: sessionId, reconnect: true }
        : { session_id: sessionId, reconnect: false, config };
      this.ws!.send(JSON.stringify(initMessage));
    };

    this.ws.onmessage = (event: MessageEvent) => {
      if (typeof event.data === 'string') {
        this.handleTextMessage(event.data);
      } else {
        this.callbacks.onAudioChunk?.(event.data as ArrayBuffer);
      }
    };

    this.ws.onclose = (event: CloseEvent) => {
      this.status.set('closed');
      const reason = GATEWAY_CLOSE_REASONS[event.code] ?? event.reason ?? 'Connexion fermée.';
      this.callbacks.onClose?.(event.code, reason);
    };

    this.ws.onerror = (event: Event) => {
      this.status.set('error');
      this.callbacks.onError?.(event);
    };
  }

  private handleTextMessage(raw: string): void {
    let message: GatewayIncomingMessage;
    try {
      message = JSON.parse(raw);
    } catch {
      console.warn('[GatewaySocket] JSON invalide ignoré :', raw);
      return;
    }

    switch (message.type) {
      case 'session_ready':
        this.status.set('ready');
        this.callbacks.onSessionReady?.();
        break;
      case 'reconnected':
        this.status.set('ready');
        this.callbacks.onReconnected?.();
        break;
      case 'transcription':
        this.callbacks.onTranscription?.(message.text);
        break;
      case 'agent_message':
        this.callbacks.onAgentMessage?.(message.text);
        break;
      case 'agent_speaking':
        this.callbacks.onAgentSpeakingStateChange?.(message.speaking);
        break;
      default:
        console.warn('[GatewaySocket] type inconnu ignoré :', message);
    }
  }

  sendAudioChunk(chunk: ArrayBuffer): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(chunk);
    }
  }

  close(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'close' }));
    }
    this.ws?.close(GatewayCloseCode.NORMAL);
    this.ws = null;
  }
}