import { CanDeactivateFn } from '@angular/router';
import { InterviewRoomComponent } from './interview-room';

export const interviewRoomGuard: CanDeactivateFn<InterviewRoomComponent> = (component) => {
  if (component.store.isCallConnected()) {
    return confirm('Un entretien est en cours. Êtes-vous sûr de vouloir quitter la salle ?');
  }
  return true;
};