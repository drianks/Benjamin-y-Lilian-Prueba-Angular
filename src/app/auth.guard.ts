import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

export const authGuard: CanActivateFn = () => {
  const router = inject(Router);

  const user = sessionStorage.getItem('loginUser');
  if (user) {
    return true;
  }

  return router.createUrlTree(['/']);
};