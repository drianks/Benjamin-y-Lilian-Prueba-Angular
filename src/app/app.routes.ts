import { Routes } from '@angular/router';

import { LoginComponent } from './login/login';
import { RegistroComponent } from './registro/registro';
import { InicioComponent } from './inicio/inicio';          // ✅ NUEVO
import { AdopcionComponent } from './adopcion/adopcion';
import { SeguimientoComponent } from './seguimiento/seguimiento';
import { SolicitudesComponent } from './solicitudes/solicitudes';
import { AboutComponent } from './about/about';

import { authGuard } from './auth.guard';

export const routes: Routes = [

  // Página inicial: login
  { path: '', component: LoginComponent },

  // Registro de usuario
  { path: 'registro', component: RegistroComponent },

  // ✅ Menú principal después de iniciar sesión
  {
    path: 'inicio',
    component: InicioComponent,
    canActivate: [authGuard]
  },

  // Crear solicitud de adopción
  {
    path: 'adopcion',
    component: AdopcionComponent,
    canActivate: [authGuard]
  },

  // Seguimiento de solicitudes (estado + registro)
  {
    path: 'seguimiento',
    component: SeguimientoComponent,
    canActivate: [authGuard]
  },

  // (Opcional) listado general si lo usas
  {
    path: 'solicitudes',
    component: SolicitudesComponent,
    canActivate: [authGuard]
  },

  // Acerca de
  { path: 'acerca', component: AboutComponent },

  // Ruta comodín
  { path: '**', redirectTo: '', pathMatch: 'full' }
];