import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class LoginComponent {

  usuario: string = '';
  password: string = '';
  mensajeError: string = '';

  constructor(private router: Router) {}

  login(): void {
    this.mensajeError = '';

    const u = this.usuario.trim();
    const p = this.password;

    if (!u || !p) {
      this.mensajeError = 'Por favor complete usuario y contraseña.';
      return;
    }

    // ✅ Usuario de prueba
    if (u === 'Benjamin' && p === '123456') {
      sessionStorage.setItem('loginUser', u);

      // ✅ AHORA VA AL MENÚ PRINCIPAL
      this.router.navigate(['/inicio']);
      return;
    }

    // ✅ Usuarios registrados
    const usuarios = JSON.parse(localStorage.getItem('usuarios') || '[]');
    const encontrado = usuarios.find(
      (x: any) => x.usuario === u && x.password === p
    );

    if (!encontrado) {
      this.mensajeError = 'Usuario o contraseña incorrectos.';
      return;
    }

    // ✅ Seguridad adicional
    if (encontrado.edad < 18) {
      this.mensajeError = 'Solo mayores de 18 años pueden ingresar.';
      return;
    }

    sessionStorage.setItem('loginUser', u);

    // ✅ AHORA VA AL MENÚ PRINCIPAL
    this.router.navigate(['/inicio']);
  }
}