export type InterviewPhase = 'intro' | 'technical' | 'situational' | 'feedback' | 'completed';

export interface TranscriptMessage {
  id: string;
  sender: 'agent' | 'candidate';
  text: string;
  timestamp: string;
  isPartial?: boolean;
}

export interface InterviewRoomState {
  phase: InterviewPhase;
  callDurationSeconds: number;
  isMuted: boolean;
  isVideoOn: boolean;
  isCallConnected: boolean;
  agentSpeaking: boolean;
  candidateSpeaking: boolean;
  transcript: TranscriptMessage[];
}