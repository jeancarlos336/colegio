"""
URL configuration for colegio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
import os
from django.http import FileResponse, HttpResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from colegioapp.views import (
    # Auth views
    home, CustomLoginView, custom_logout_view, dashboard, dashboard_profesor,
    
    # Usuario views
    crear_usuario, detalle_usuario, editar_usuario, eliminar_usuario, lista_usuarios,
    
    # Sede views
    lista_sedes, crear_sede, editar_sede, eliminar_sede,
    
    # Curso views
    lista_cursos, crear_curso, detalle_curso, editar_curso, eliminar_curso,
    
    # Asignatura views
    lista_asignaturas, crear_asignatura, detalle_asignatura, 
    editar_asignatura, eliminar_asignatura,
    
    # Día views
    DiaSemanaListView, DiaSemanaCreateView, DiaSemanaUpdateView, DiaSemanaDeleteView,
    
    # Matrícula views
    MatriculaListView, MatriculaDetailView, MatriculaCreateView, 
    MatriculaUpdateView, MatriculaDeleteView,
    
    # Asignación views
    AsignacionListView, AsignacionCreateView, AsignacionUpdateView, AsignacionDeleteView,
    
    # Calificación views
    lista_calificaciones, eliminar_calificacion,
    seleccionar_curso_calificacion, ingresar_calificaciones,
    
    # Horario views
    horario_lista, horario_crear, horario_editar, horario_eliminar,
    
    # Pago views
    lista_pagos_mensualidad, crear_pago_mensualidad, editar_pago_mensualidad,
    eliminar_pago_mensualidad, generar_voucher_pdf,
    
    #Anotaciones
    lista_anotaciones,detalle_anotacion,EditarAnotacionView,eliminar_anotacion,CrearAnotacionView, get_alumnos_curso,
    
    # Asistencia views
    tomar_asistencia, seleccionar_curso,ListarAsistenciaView, EliminarAsistenciaView,EditarAsistenciaView,    

    #evaluciones
    EvaluacionListView, EvaluacionCreateView, EvaluacionDetailView, EvaluacionUpdateView, EvaluacionDeleteView, TodasEvaluacionListView,  
    
    #bitacora
    crear_bitacora,
    
    # Informes views
    seleccionar_parametros_informe,
    generar_informe_notas,
    generar_informe_notas_alumno,
    seleccionar_parametros_informe_alumno,
    CertificadoView,
    load_alumnos,
    load_alumnos_notas,
    generar_informe,
    
)


def serve_pdf(request, pago_id):
    pdf_path = os.path.join(settings.MEDIA_ROOT, f'vouchers/voucher_{pago_id}.pdf')
    if os.path.exists(pdf_path):
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    return HttpResponse('PDF no encontrado', status=404)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth URLs
    path('', home, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),

    # Usuario URLs
    path('usuarios/listar/', lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', crear_usuario, name='crear_usuario'),
    path('usuarios/<int:pk>/', detalle_usuario, name='detalle_usuario'),
    path('usuarios/<int:pk>/editar/', editar_usuario, name='editar_usuario'),
    path('usuarios/<int:pk>/eliminar/', eliminar_usuario, name='eliminar_usuario'),

    # Sede URLs
    path('sedes/', lista_sedes, name='lista_sedes'),
    path('sedes/crear/', crear_sede, name='crear_sede'),
    path('sedes/editar/<int:pk>/', editar_sede, name='editar_sede'),
    path('sedes/eliminar/<int:pk>/', eliminar_sede, name='eliminar_sede'),

    # Curso URLs
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('cursos/crear/', crear_curso, name='crear_curso'),
    path('cursos/<int:curso_id>/', detalle_curso, name='detalle_curso'),
    path('cursos/<int:curso_id>/editar/', editar_curso, name='editar_curso'),
    path('cursos/<int:curso_id>/eliminar/', eliminar_curso, name='eliminar_curso'),

    # Asignatura URLs
    path('asignaturas/', lista_asignaturas, name='lista_asignaturas'),
    path('asignaturas/nueva/', crear_asignatura, name='crear_asignatura'),
    path('asignaturas/<int:pk>/', detalle_asignatura, name='detalle_asignatura'),
    path('asignaturas/<int:pk>/editar/', editar_asignatura, name='editar_asignatura'),
    path('asignaturas/<int:pk>/eliminar/', eliminar_asignatura, name='eliminar_asignatura'),

    # Día URLs
    path('dias/', DiaSemanaListView.as_view(), name='lista_dias'),
    path('dias/nuevo/', DiaSemanaCreateView.as_view(), name='crear_dia'),
    path('dias/editar/<int:pk>/', DiaSemanaUpdateView.as_view(), name='editar_dia'),
    path('dias/eliminar/<int:pk>/', DiaSemanaDeleteView.as_view(), name='eliminar_dia'),

    # Matrícula URLs
    path('matriculas/', MatriculaListView.as_view(), name='lista_matriculas'),
    path('matriculas/nueva/', MatriculaCreateView.as_view(), name='crear_matricula'),
    path('matriculas/<int:pk>/', MatriculaDetailView.as_view(), name='detalle_matricula'),
    path('matriculas/<int:pk>/editar/', MatriculaUpdateView.as_view(), name='editar_matricula'),
    path('matriculas/<int:pk>/eliminar/', MatriculaDeleteView.as_view(), name='eliminar_matricula'),

    # Asignación URLs
    path('asignaciones/', AsignacionListView.as_view(), name='asignacion_list'),
    path('asignaciones/crear/', AsignacionCreateView.as_view(), name='asignacion_create'),
    path('asignaciones/<int:pk>/editar/', AsignacionUpdateView.as_view(), name='asignacion_update'),
    path('asignaciones/<int:pk>/eliminar/', AsignacionDeleteView.as_view(), name='asignacion_delete'),

    # Calificación URLs
    path('calificaciones/', lista_calificaciones, name='lista_calificaciones'),
    path('calificaciones/eliminar/<int:calificacion_id>/', eliminar_calificacion, name='eliminar_calificacion'),
    path('calificaciones/seleccionar/', seleccionar_curso_calificacion, name='seleccionar_curso_calificacion'),
    path('calificaciones/ingresar/', ingresar_calificaciones, name='ingresar_calificaciones'),

    # Horario URLs
    path('horarios/', horario_lista, name='horario_lista'),
    path('horarios/crear/', horario_crear, name='horario_crear'),
    path('horarios/editar/<int:pk>/', horario_editar, name='horario_editar'),
    path('horarios/eliminar/<int:pk>/', horario_eliminar, name='horario_eliminar'),

    # Pago URLs
    path('pagos-mensualidad/', lista_pagos_mensualidad, name='lista_pagos_mensualidad'),
    path('pagos-mensualidad/crear/', crear_pago_mensualidad, name='crear_pago_mensualidad'),
    path('pagos-mensualidad/editar/<int:pk>/', editar_pago_mensualidad, name='editar_pago_mensualidad'),
    path('pagos-mensualidad/eliminar/<int:pk>/', eliminar_pago_mensualidad, name='eliminar_pago_mensualidad'),
    path('voucher/<int:pago_id>/', generar_voucher_pdf, name='generar_voucher_pdf'),

    # Asistencia URLs
    path('asistencia/seleccionar/', seleccionar_curso, name='seleccionar_curso'),
    path('asistencia/tomar/', tomar_asistencia, name='tomar_asistencia'),
    path('editar-asistencia/<int:pk>/', EditarAsistenciaView.as_view(), name='editar_asistencia'),
    path('asistencia/', ListarAsistenciaView.as_view(), name='listar_asistencia'),
    path('asistencia/eliminar/<int:pk>/', EliminarAsistenciaView.as_view(), name='eliminar_asistencia'),

    # Informes URLs
   
    path('informes/notas-asignatura/', seleccionar_parametros_informe, name='seleccionar_parametros_informe'),
    path('informes/notas-asignatura/generar/<int:asignatura_id>/<int:año>/<int:semestre>/', 
         generar_informe_notas, name='generar_informe_notas'),
    
    path('informes/alumno/', seleccionar_parametros_informe_alumno, name='seleccionar_parametros_informe_alumno'),
    path('ajax/load-alumnos-notas/', load_alumnos_notas, name='ajax_load_alumnos_notas'),
    path('informes/alumno/<int:alumno_id>/<int:año>/<int:semestre>/', generar_informe_notas_alumno, name='generar_informe_notas_alumno'),
   
    
    path('informes/certificado/', CertificadoView.as_view(), name='certificado_form'),
    path('ajax/load-alumnos/', load_alumnos, name='ajax_load_alumnos'),
    
    
    #asistencia
    path('generar_informe/', generar_informe, name='generar_informe'),
    
    path('pdf/<int:pago_id>/', serve_pdf, name='serve_pdf'),
   
   
   #evalucioens
    path('evaluaciones/', EvaluacionListView.as_view(), name='evaluacion_list'),
    path('evaluaciones/crear/', EvaluacionCreateView.as_view(), name='evaluacion_create'),
    path('evaluaciones/<int:pk>/', EvaluacionDetailView.as_view(), name='evaluacion_detail'),
    path('evaluaciones/<int:pk>/editar/', EvaluacionUpdateView.as_view(), name='evaluacion_update'),
    path('evaluaciones/<int:pk>/eliminar/', EvaluacionDeleteView.as_view(), name='evaluacion_delete'),
    path('evaluaciones/otras/', TodasEvaluacionListView.as_view(), name='evaluacion_otras'),


    path('dashboard/profesor/', dashboard_profesor, name='dashboard_profesor'),
    
    
    path('anotaciones/', lista_anotaciones, name='lista_anotaciones'),
    path('anotaciones/<int:pk>/', detalle_anotacion, name='detalle_anotacion'),

    path('editar_anotacion/<int:pk>/', EditarAnotacionView.as_view(), name='editar_anotacion'),
    path('anotaciones/<int:pk>/eliminar/', eliminar_anotacion, name='eliminar_anotacion'),


    path('anotacion/crear/', CrearAnotacionView.as_view(), name='crear_anotacion'),
    path('api/alumnos-por-curso/', get_alumnos_curso, name='alumnos_por_curso'),
    
    path('bitacora/crear/', crear_bitacora, name='crear_bitacora'),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

