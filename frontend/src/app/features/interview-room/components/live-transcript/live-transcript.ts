import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranscriptMessage } from '../../interview-room.models';

@Component({
  selector: 'app-live-transcript',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './live-transcript.html',
  styleUrl: './live-transcript.scss',
})
export class LiveTranscript {
  readonly transcript = input.required<TranscriptMessage[]>();
}