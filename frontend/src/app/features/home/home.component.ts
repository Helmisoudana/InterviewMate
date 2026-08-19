import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AvatarComponent } from '../../shared/ui/avatar/avatar.component';

interface HistoryPreviewItem {
  id: string;
  role: string;
  date: string;
  score: number | null; // null = rapport en cours de génération
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink, AvatarComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent {
  readonly recentInterviews = signal<HistoryPreviewItem[]>([
    { id: '1', role: 'Développeur Frontend Angular', date: '14 août 2026', score: 82 },
    { id: '2', role: 'Product Manager', date: '10 août 2026', score: 74 },
    { id: '3', role: 'Data Analyst', date: '5 août 2026', score: null },
  ]);
}