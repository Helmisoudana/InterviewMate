import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  readonly isAuthenticated = signal<boolean>(false);
  readonly token = signal<string | null>(null);
}