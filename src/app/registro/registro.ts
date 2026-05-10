import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-registro',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './registro.html',
  styleUrls: ['./registro.css']
})
export class RegistroComponent {

  usuario: string = '';
  fechaNacimiento: string = ''; // formato: YYYY-MM-DD
  password: string = '';
  password2: string = '';

  edadCalculada: number | null = null;

  mensajeError: string = '';
  mensajeOk: string = '';

  constructor(private router: Router) {}

  // Calcula edad exacta en años (años cumplidos) desde YYYY-MM-DD
  private calcularEdad(yyyyMmDd: string): number {
    // parseo local para evitar desfases por zona horaria en algunos entornos [7](https://www.calculate-age.online/en/blog/how-to-calculate-age-in-javascript-date-object-and-day-js-examples/)
    const [y, m, d] = yyyyMmDd.split('-').map(Number);
    const nacimiento = new Date(y, m - 1, d);
    const hoy = new Date();

    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const diffMes = hoy.getMonth() - nacimiento.getMonth();

    if (diffMes < 0 || (diffMes === 0 && hoy.getDate() < nacimiento.getDate())) {
      edad--;
    }

    return edad; // lógica estándar de edad cumplida [1](https://www.slingacademy.com/article/calculating-age-or-time-spans-from-birthdates-in-javascript/)[2](https://stackoverflow.com/questions/4076321/javascript-age-calculation)
  }

  registrar() {
    this.mensajeError = '';
    this.mensajeOk = '';
    this.edadCalculada = null;

    // Validación de campos
    if (!this.usuario || !this.fechaNacimiento || !this.password || !this.password2) {
      this.mensajeError = 'Por favor complete todos los campos.';
      return;
    }

    // Contraseña
    if (this.password.length < 6) {
      this.mensajeError = 'La contraseña debe tener al menos 6 caracteres.';
      return;
    }

    if (this.password !== this.password2) {
      this.mensajeError = 'Las contraseñas no coinciden.';
      return;
    }

    // Edad exacta por fecha nacimiento
    const edad = this.calcularEdad(this.fechaNacimiento);
    this.edadCalculada = edad;

    if (edad < 18) {
      this.mensajeError = 'Debes ser mayor de 18 años para registrarte como adoptante.';
      return;
    }

    // Guardar usuario
    const usuarios = JSON.parse(localStorage.getItem('usuarios') || '[]');

    const existe = usuarios.find((u: any) => u.usuario === this.usuario.trim());
    if (existe) {
      this.mensajeError = 'Ese usuario ya existe.';
      return;
    }

    usuarios.push({
      usuario: this.usuario.trim(),
      password: this.password,
      fechaNacimiento: this.fechaNacimiento,
      edad: edad
    });

    localStorage.setItem('usuarios', JSON.stringify(usuarios));

    this.mensajeOk = 'Usuario registrado correctamente. Volviendo al inicio de sesión...';

    // limpiar
    this.usuario = '';
    this.fechaNacimiento = '';
    this.password = '';
    this.password2 = '';

    setTimeout(() => {
      this.router.navigate(['/']);
    }, 1500);
  }
}
