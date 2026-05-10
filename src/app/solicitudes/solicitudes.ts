import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-solicitudes',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './solicitudes.html',
  styleUrls: ['./solicitudes.css']
})
export class SolicitudesComponent {

  solicitudes: any[] = [];

  constructor(private router: Router) {}

  ngOnInit(): void {
    const todas = JSON.parse(localStorage.getItem('solicitudes') || '[]');
    const usuario = sessionStorage.getItem('loginUser');

    // ✅ Mostrar solo las solicitudes del usuario logueado
    this.solicitudes = todas.filter(
      (s: any) => s.usuarioSistema === usuario
    );

    // ✅ Ordenar de más reciente a más antigua
    this.solicitudes.sort((a: any, b: any) => (b.id || 0) - (a.id || 0));
  }

  // ✅ Eliminar solicitud (permitido mientras esté en evaluación)
  eliminarSolicitud(index: number): void {
    if (!confirm('¿Estás seguro de eliminar esta solicitud?')) return;

    this.solicitudes.splice(index, 1);
    localStorage.setItem('solicitudes', JSON.stringify(this.solicitudes));
  }
}