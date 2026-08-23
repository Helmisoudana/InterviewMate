import { Routes } from '@angular/router';
import { interviewRoomGuard } from './features/interview-room/interview-room-guard';

export const routes: Routes = [
  // 1. Page de connexion (Page par défaut)
  {
    path: '',
    loadComponent: () =>
      import('./features/auth/login/login').then((m) => m.LoginComponent),
    title: 'InterviewMate — Connexion',
  },

  // 2. Page d'inscription
  {
    path: 'register',
    loadComponent: () =>
      import('./features/auth/register/register').then((m) => m.RegisterComponent),
    title: 'InterviewMate — Inscription',
  },

  // 3. Espace principal (AppShell) : Contient l'Accueil et l'Historique
  {
    path: 'home',
    loadComponent: () =>
      import('./core/layout/app-shell/app-shell.component').then(
        (m) => m.AppShellComponent
      ),
    children: [
      {
        path: '',
        pathMatch: 'full',
        loadComponent: () =>
          import('./features/home/home.component').then(
            (m) => m.HomeComponent
          ),
        title: 'InterviewMate — Accueil',
      },
      {
        path: 'history',
        loadComponent: () =>
          import('./features/interview-history/interview-history').then(
            (m) => m.InterviewHistoryComponent
          ),
        title: 'InterviewMate — Historique des entretiens',
      },
    ],
  },

  // 4. Configuration de l'entretien (Poste, Durée, Difficulté, Langue)
  {
    path: 'setup',
    loadComponent: () =>
      import('./features/interview-setup/interview-setup').then(
        (m) => m.InterviewSetupComponent
      ),
    title: "InterviewMate — Configuration de l'entretien",
  },

  {
    path: 'pre-call',
    loadComponent: () =>
      import('./features/pre-call/pre-call').then((m) => m.PreCallComponent),
    title: 'InterviewMate — Vérification du matériel',
  },

  {
    path: 'interview',
    loadComponent: () =>
      import('./features/interview-room/interview-room').then(
        (m) => m.InterviewRoomComponent
      ),
    canDeactivate: [interviewRoomGuard],
    title: "InterviewMate — Salle d'entretien",
  },

  {
    path: 'interview/end',
    loadComponent: () =>
      import('./features/interview-end/interview-end').then(
        (m) => m.InterviewEndComponent
      ),
    title: 'InterviewMate — Entretien terminé',
  },

  { path: '**', redirectTo: '' },
];