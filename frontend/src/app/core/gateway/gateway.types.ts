export type DureeEntretien = 'COURTE' | 'MOYENNE' | 'LONGUE';

export type DifficulteEntretien = 'FACILE' | 'MOYEN' | 'DIFFICILE';

export const DUREE_OPTIONS: ReadonlyArray<{ value: DureeEntretien; label: string }> = [
  { value: 'COURTE', label: 'Courte' },
  { value: 'MOYENNE', label: 'Moyenne' },
  { value: 'LONGUE', label: 'Longue' },
];

export const DIFFICULTE_OPTIONS: ReadonlyArray<{ value: DifficulteEntretien; label: string }> = [
  { value: 'FACILE', label: 'Facile' },
  { value: 'MOYEN', label: 'Moyen' },
  { value: 'DIFFICILE', label: 'Difficile' },
];

export interface InterviewConfig {
  poste: string;
  langue: string;
  duree: DureeEntretien;
  difficulte: DifficulteEntretien;
}

export interface GatewayInitMessage {
  session_id: string;
  reconnect: boolean;
  config?: InterviewConfig;
}

export type GatewayOutgoingAudioChunk = ArrayBuffer;

export interface GatewayCloseMessage {
  type: 'close';
}

export type GatewayOutgoingControlMessage = GatewayCloseMessage;

export interface GatewaySessionReadyMessage {
  type: 'session_ready';
}

export interface GatewayReconnectedMessage {
  type: 'reconnected';
}

export interface GatewayTranscriptionMessage {
  type: 'transcription';
  text: string;
}

export interface GatewayAgentMessage {
  type: 'agent_message';
  text: string;
}

export interface GatewayAgentSpeakingMessage {
  type: 'agent_speaking';
  speaking: boolean;
}

export type GatewayIncomingMessage =
  | GatewaySessionReadyMessage
  | GatewayReconnectedMessage
  | GatewayTranscriptionMessage
  | GatewayAgentMessage
  | GatewayAgentSpeakingMessage;

export type GatewayIncomingAudioChunk = ArrayBuffer | Blob;

export enum GatewayCloseCode {
  NORMAL = 1000,
  INIT_INVALIDE = 4000,
  SESSION_INVALIDE = 4001,
  CONFIG_INVALIDE = 4002,
  RECONNEXION_INTROUVABLE = 4004,
}

export const GATEWAY_CLOSE_REASONS: Record<number, string> = {
  [GatewayCloseCode.NORMAL]: 'Entretien terminé.',
  [GatewayCloseCode.INIT_INVALIDE]: "Échec de connexion : message d'initialisation invalide.",
  [GatewayCloseCode.SESSION_INVALIDE]: 'Échec de connexion : session invalide ou expirée.',
  [GatewayCloseCode.CONFIG_INVALIDE]: "Configuration d'entretien invalide.",
  [GatewayCloseCode.RECONNEXION_INTROUVABLE]: 'Aucune session à reconnecter.',
};

export type GatewayConnectionStatus =
  | 'idle'
  | 'connecting'
  | 'ready'
  | 'reconnecting'
  | 'closed'
  | 'error';