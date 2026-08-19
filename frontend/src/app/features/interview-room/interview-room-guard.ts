import { CanActivateFn } from '@angular/router';

export const interviewRoomGuard: CanActivateFn = (route, state) => {
  return true;
};
