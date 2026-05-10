import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-adopcion',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './adopcion.html',
  styleUrls: ['./adopcion.css']
})
export class AdopcionComponent {

  // ✅ PREFERENCIAS DE ADOPCIÓN
  preferencias = {
    tipoMascota: '',
    tamano: 'Indistinto',
    edad: 'Indistinta',
    sexo: 'Indistinto',
    aceptaMestizo: 'Sí'
  };

  // ✅ DATOS DEL RESPONSABLE
  adoptante = {
    nombreCompleto: '',
    rut: '',
    telefono: '',
    email: '',
    direccion: '',
    comuna: '',
    region: '',
    comentarios: ''
  };

  rutInvalido = false;
  mensajeOk = '';
  mensajeError = '';
  enviando = false;

  constructor(private router: Router) {}

  // ========= VALIDACIÓN RUT =========
  private limpiarRut(rut: string): string {
    return String(rut).replace(/[.\-\s]/g, '').toUpperCase();
  }

  private calcularDV(cuerpo: string): string {
    let suma = 0;
    let multiplo = 2;

    for (let i = cuerpo.length - 1; i >= 0; i--) {
      suma += parseInt(cuerpo[i], 10) * multiplo;
      multiplo = multiplo === 7 ? 2 : multiplo + 1;
    }

    const dv = 11 - (suma % 11);
    if (dv === 11) return '0';
    if (dv === 10) return 'K';
    return String(dv);
  }

  private esRutValido(rut: string): boolean {
    const limpio = this.limpiarRut(rut);
    if (limpio.length < 2) return false;

    const cuerpo = limpio.slice(0, -1);
    const dvIngresado = limpio.slice(-1);

    if (!/^\d+$/.test(cuerpo)) return false;
    return dvIngresado === this.calcularDV(cuerpo);
  }

  validarRutEnBlur(): void {
    if (!this.adoptante.rut) {
      this.rutInvalido = false;
      return;
    }
    this.rutInvalido = !this.esRutValido(this.adoptante.rut);
  }

  // ========= GUARDAR SOLICITUD =========
  guardarSolicitud(): void {
    if (this.enviando) return;

    this.mensajeError = '';
    this.mensajeOk = '';

    if (!this.preferencias.tipoMascota) {
      this.mensajeError = 'Debe indicar qué tipo de mascota desea adoptar.';
      return;
    }

    if (
      !this.adoptante.nombreCompleto ||
      !this.adoptante.rut ||
      !this.adoptante.telefono ||
      !this.adoptante.email ||
      !this.adoptante.direccion ||
      !this.adoptante.comuna ||
      !this.adoptante.region
    ) {
      this.mensajeError = 'Debe completar todos los datos del responsable.';
      return;
    }

    if (!this.esRutValido(this.adoptante.rut)) {
      this.rutInvalido = true;
      this.mensajeError = 'El RUT ingresado no es válido.';
      return;
    }

    this.enviando = true;

    const solicitudes = JSON.parse(localStorage.getItem('solicitudes') || '[]');
    const usuarioSistema = sessionStorage.getItem('loginUser') || '';

    solicitudes.push({
      id: Date.now(),
      preferencias: this.preferencias,
      adoptante: this.adoptante,
      usuarioSistema,
      estado: 'En evaluación',
      fechaRegistro: new Date().toLocaleDateString('es-CL')
    });

    localStorage.setItem('solicitudes', JSON.stringify(solicitudes));

    this.mensajeOk = 'Solicitud enviada correctamente 🐾';

    setTimeout(() => {
      this.enviando = false;
      this.router.navigate(['/seguimiento']);
    }, 800);
  }
}