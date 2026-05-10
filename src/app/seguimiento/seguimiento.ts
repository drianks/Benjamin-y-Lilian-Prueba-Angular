import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-seguimiento',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './seguimiento.html',
  styleUrls: ['./seguimiento.css']
})
export class SeguimientoComponent {

  solicitudes: any[] = [];

  // Flujo del proceso (solo informativo)
  pasos: string[] = [
    'En evaluación',
    'Contacto pendiente',
    'Visita domiciliaria',
    'Aprobada',
    'Finalizada'
  ];

  constructor(private router: Router) {}

  ngOnInit(): void {
    const todas = JSON.parse(localStorage.getItem('solicitudes') || '[]');
    const usuario = sessionStorage.getItem('loginUser');

    // ✅ Mostrar solo solicitudes del usuario logueado
    this.solicitudes = todas.filter(
      (s: any) => s.usuarioSistema === usuario
    );

    // ✅ Ordenar de más reciente a más antigua
    this.solicitudes.sort((a: any, b: any) => (b.id || 0) - (a.id || 0));
  }

  // ---------- DESCRIPCIÓN DE ESTADO ----------
  descripcionEstado(estado: string): string {
    switch (estado) {
      case 'En evaluación':
        return 'Estamos revisando la información registrada.';
      case 'Contacto pendiente':
        return 'Falta información o validación. Te contactaremos.';
      case 'Visita domiciliaria':
        return 'Se coordinará una visita para completar la evaluación.';
      case 'Aprobada':
        return 'Solicitud aprobada. Se coordinará la adopción.';
      case 'Finalizada':
        return 'Proceso finalizado. ¡Gracias por adoptar!';
      default:
        return 'Estado registrado.';
    }
  }

  // ---------- PASO ACTUAL ----------
  indicePaso(estado: string): number {
    const idx = this.pasos.indexOf(estado);
    return idx === -1 ? 0 : idx;
  }

  // ---------- ELIMINAR SOLICITUD ----------
  eliminarSolicitud(index: number): void {
    if (!confirm('¿Estás seguro de eliminar esta solicitud?')) return;

    this.solicitudes.splice(index, 1);
    localStorage.setItem('solicitudes', JSON.stringify(this.solicitudes));
  }
}