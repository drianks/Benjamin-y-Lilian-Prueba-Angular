import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-inicio',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './inicio.html',
  styleUrls: ['./inicio.css']
})
export class InicioComponent {

  constructor(private router: Router) {}

  irAdopcion(): void {
    this.router.navigate(['/adopcion']);
  }

  irSeguimiento(): void {
    this.router.navigate(['/seguimiento']);
  }

  cerrarSesion(): void {
    sessionStorage.removeItem('loginUser');
    this.router.navigate(['/']);
  }
}