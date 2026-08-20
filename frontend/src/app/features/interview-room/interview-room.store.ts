import { Injectable, signal, computed, OnDestroy } from '@angular/core';
import { InterviewRoomState, InterviewPhase, TranscriptMessage } from './interview-room.models';

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

@Injectable()
export class InterviewRoomStore implements OnDestroy {
  private readonly _state = signal<InterviewRoomState>(INITIAL_STATE);

  readonly phase = computed(() => this._state().phase);
  readonly callDurationSeconds = computed(() => this._state().callDurationSeconds);
  readonly isMuted = computed(() => this._state().isMuted);
  readonly isVideoOn = computed(() => this._state().isVideoOn);
  readonly isCallConnected = computed(() => this._state().isCallConnected);
  readonly agentSpeaking = computed(() => this._state().agentSpeaking);
  readonly candidateSpeaking = computed(() => this._state().candidateSpeaking);
  readonly transcript = computed(() => this._state().transcript);

  readonly formattedDuration = computed(() => {
    const totalSeconds = this.callDurationSeconds();
    const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
    const seconds = (totalSeconds % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  });

  private timerInterval: any = null;
  private simulationTimeout: any = null;

  toggleMute(): void {
    this._state.update((s) => ({ ...s, isMuted: !s.isMuted }));
  }

  toggleVideo(): void {
    this._state.update((s) => ({ ...s, isVideoOn: !s.isVideoOn }));
  }

  startSession(): void {
    if (this._state().isCallConnected) return;

    this._state.update((s) => ({ ...s, isCallConnected: true }));

    this.timerInterval = setInterval(() => {
      this._state.update((s) => ({
        ...s,
        callDurationSeconds: s.callDurationSeconds + 1,
      }));
    }, 1000);

    this.runMockSimulation();
  }

  endCall(): void {
    if (this.timerInterval) clearInterval(this.timerInterval);
    if (this.simulationTimeout) clearTimeout(this.simulationTimeout);

    this._state.update((s) => ({
      ...s,
      isCallConnected: false,
      phase: 'completed',
      agentSpeaking: false,
      candidateSpeaking: false,
    }));
  }

  private runMockSimulation(): void {
    const scenarioSequence = [
      {
        delay: 1000,
        action: () => {
          this.setAgentSpeaking(true);
          this.addMessage('agent', 'Bonjour ! Je suis ravi de vous rencontrer. Pouvez-vous vous présenter brièvement ?');
        },
      },
      {
        delay: 4000,
        action: () => {
          this.setAgentSpeaking(false);
          this.setCandidateSpeaking(true);
          this.addMessage('candidate', 'Bonjour ! Je suis développeur Frontend spécialisé en Angular...');
        },
      },
      {
        delay: 8000,
        action: () => {
          this.setCandidateSpeaking(false);
          this.setPhase('technical');
          this.setAgentSpeaking(true);
          this.addMessage('agent', 'Parfait. Passons à la partie technique : Comment fonctionnent les Signals dans Angular ?');
        },
      },
      {
        delay: 13000,
        action: () => {
          this.setAgentSpeaking(false);
          this.setCandidateSpeaking(true);
          this.addMessage('candidate', 'Les Signals apportent une réactivité à granularité fine sans dépendre de Zone.js...');
        },
      },
      {
        delay: 18000,
        action: () => {
          this.setCandidateSpeaking(false);
          this.setPhase('situational');
          this.setAgentSpeaking(true);
          this.addMessage('agent', 'Excellente explication. Une question de mise en situation maintenant...');
        },
      },
    ];

    let currentStep = 0;
    const executeNextStep = () => {
      if (currentStep < scenarioSequence.length && this._state().isCallConnected) {
        const step = scenarioSequence[currentStep];
        this.simulationTimeout = setTimeout(() => {
          step.action();
          currentStep++;
          executeNextStep();
        }, step.delay);
      }
    };

    executeNextStep();
  }

  private setPhase(phase: InterviewPhase): void {
    this._state.update((s) => ({ ...s, phase }));
  }

  private setAgentSpeaking(speaking: boolean): void {
    this._state.update((s) => ({ ...s, agentSpeaking: speaking }));
  }

  private setCandidateSpeaking(speaking: boolean): void {
    this._state.update((s) => ({ ...s, candidateSpeaking: speaking }));
  }

  private addMessage(sender: 'agent' | 'candidate', text: string): void {
    const newMessage: TranscriptMessage = {
      id: Date.now().toString(),
      sender,
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    this._state.update((s) => ({
      ...s,
      transcript: [...s.transcript, newMessage],
    }));
  }

  ngOnDestroy(): void {
    this.endCall();
  }
}