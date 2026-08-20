import {
  Component,
  OnInit,
  input,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-agent-tile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './agent-tile.html',
  styleUrl: './agent-tile.scss',
})
export class AgentTile implements OnInit {
  readonly isSpeaking = input<boolean>(false);
  imageLoaded = signal<boolean>(false);

  // Chemin vers votre fichier WebP
  readonly avatarSource = 'interview.webp';

  constructor() {}

  ngOnInit(): void {}

  onImageLoad(): void {
    this.imageLoaded.set(true);
  }

  onImageError(event?: Event): void {
    console.error(`[AgentTile] Impossible de charger l'image : ${this.avatarSource}`, event);
    this.imageLoaded.set(false);
  }
}