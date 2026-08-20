import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class RegisterComponent {
  private readonly router = inject(Router);

  email = '';
  username = '';
  password = '';

  onSubmit(): void {
    // Validation instantanée et redirection vers l'accueil
    this.router.navigate(['/login']);
  }
}