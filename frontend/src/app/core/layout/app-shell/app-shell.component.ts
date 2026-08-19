import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { BadgeStatusComponent } from '../../../shared/ui/badge-status/badge-status.component';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterOutlet, BadgeStatusComponent],
  templateUrl: './app-shell.component.html',
  styleUrl: './app-shell.component.scss',
})
export class AppShellComponent {}