
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Sede, Usuario, Curso, Matricula,Asignatura,DiaSemana,AsignacionProfesorSede,Calificacion,Horario,PagoMensualidad,RegistroAsistencia
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import UsuarioForm,EditarUsuarioForm,InformeAsistenciaForm,SedeForm,CalificacionFormSet, CertificadoForm,CursoForm,ParametrosInformeAlumnoForm,ParametrosInformeForm,CalificacionSeleccionForm,AsignaturaForm,DiaSemanaForm,AsistenciaSeleccionForm,RegistroAsistenciaFormSet,MatriculaForm,AsignacionForm,HorarioForm, HorarioFiltroForm,PagoMensualidadForm, PagoMensualidadFiltroForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,DetailView,FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q
from django.utils import timezone
import os
from django.http import FileResponse, HttpResponse, Http404
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import urlencode
from django.utils.timezone import now
from django.forms import modelformset_factory
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
from decimal import Decimal
from django.http import JsonResponse
from datetime import datetime, date
from django.views import View
from collections import defaultdict
import calendar
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from django.http import HttpResponse
from openpyxl.utils import get_column_letter





def home(request):
    """Vista de página principal antes de iniciar sesión"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect(reverse_lazy('login'))


# Vista personalizada para el login (verifica si el usuario ya está autenticado)  

class CustomLoginView(LoginView):
    template_name = "colegio/login.html"  # Ruta correcta para la plantilla

    def get_redirect_url(self):
        # Si el usuario ya está autenticado, redirige al dashboard
        if self.request.user.is_authenticated:
            return reverse_lazy("dashboard")
        
        # Si no está autenticado, usa la URL por defecto
        return super().get_redirect_url()



# Vista personalizada para el logout (cerrar sesión)
def custom_logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('login')  # Redirige a la página de login después de cerrar sesión


@login_required
def dashboard(request):
    """Vista del panel de control principal"""
    
    # Obtener estadísticas generales para todos los roles
    total_usuarios = Usuario.objects.count()
    total_cursos = Curso.objects.count()
    total_matriculas = Matricula.objects.count()

    
 
    # Definir los menús específicos para cada rol con la estructura correcta
    menus = {
        'ADMIN': [
            {
                'label': 'Usuarios',
                'url': 'lista_usuarios',  # Este nombre coincide con tu urls.py
                'icon': 'fa-users',
                'submenu': [
                    {'name': 'Listar Usuarios', 'url': 'lista_usuarios'},  # '/usuarios/listar/'
                    {'name': 'Crear Usuario', 'url': 'crear_usuario'},     # '/usuarios/crear/'
                ]
            },
            {
                'label': 'Sedes',
                'url': 'lista_sedes',  # Agregando otra sección del menú basada en tus URLs
                'icon': 'fa-building',
                'submenu': [
                    {'name': 'Listar Sedes', 'url': 'lista_sedes'},
                    {'name': 'Crear Sede', 'url': 'crear_sede'},
                ]
            },
            {
                'label': 'Cursos',
                'url': 'lista_cursos',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Listar Cursos', 'url': 'lista_cursos'},
                    {'name': 'Crear Curso', 'url': 'crear_curso'},
                ]
            },
            {
                'label': 'Asignaturas',
                'url': 'lista_asignaturas',
                'icon': 'fa fa-bookmark',
                'submenu': [
                    {'name': 'Listar Asignatura', 'url': 'lista_asignaturas'},
                    {'name': 'Crear Asignatura', 'url': 'crear_asignatura'},
                ]
            },
            {
                'label': 'Dias',
                'url': 'lista_dias',
                'icon': 'fa fa-calendar',
                'submenu': [
                    {'name': 'Listar Dias', 'url': 'lista_dias'},
                    {'name': 'Crear Dias', 'url': 'crear_dia'},
                ]
            },
            {
                'label': 'Matriculas',
                'url': 'lista_matriculas',
                'icon': 'fa fa-pencil',
                'submenu': [
                    {'name': 'Listar Matriculas', 'url': 'lista_matriculas'},
                    {'name': 'Crear Matriculas', 'url': 'crear_matricula'},
                ]
            },
            {
                'label': 'Profesor - Sede',
                'url': 'asignacion_list',
                'icon':'bi bi-person-rolodex',
                'submenu': [
                    {'name': 'Asignar Profesor Sede', 'url': 'asignacion_list'},
                    {'name': 'Crear Asignacion', 'url': 'asignacion_create'},
                ]
            },
            {
                'label': 'Calificaciones',
                'url': 'lista_calificaciones',
                'icon': 'fa fa-check-square',
                'submenu': [
                    {'name': 'Listar Calificaciones', 'url': 'lista_calificaciones'},
                    {'name': 'Asignar Calificaciones', 'url': 'seleccionar_curso_calificacion'},
                ]
            },
            {
                'label': 'Horario de Clases',
                'url': 'horario_lista',
                'icon': 'fa fa-calendar',
                'submenu': [
                    {'name': 'Listar Horarios', 'url': 'horario_lista'},
                    {'name': 'Crear Horaio', 'url': 'horario_crear'},
                ]
            },
            {
                'label': 'Pago Escolaridad',
                'url': 'lista_pagos_mensualidad',
                'icon': 'fa fa-cart-arrow-down',
                'submenu': [
                    {'name': 'Listado de Pagos', 'url': 'lista_pagos_mensualidad'},
                    {'name': 'Crear Pagos', 'url': 'crear_pago_mensualidad'},
                ]
            },
            {
                'label': 'Asitencia',
                'url': 'seleccionar_curso',
                'icon': 'fa fa-th',
                'submenu': [
                    {'name': 'Tomar Asistencia', 'url': 'seleccionar_curso'},                    
                ]
            },
            {
                'label': 'Informes',
                'url': 'menu_informes',
                'icon': 'fa fa-print',
                'submenu': [
                    {'name': 'Informe Notas x Asignatura', 'url': 'seleccionar_parametros_informe'},
                    {'name': 'Informe Notas x Alumnos', 'url': 'seleccionar_parametros_informe_alumno'},
                    {'name': 'Certificado Alumno Regular', 'url': 'certificado_form'},
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},
                    
                    
                ]
            }         
        ],

        'PROFESOR': [
            {
                'label': 'Calificaciones',
                'url': 'lista_calificaciones',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Listar Calificaciones', 'url': 'lista_calificaciones'},
                    {'name': 'Asignar Calificaciones', 'url': 'seleccionar_curso_calificacion'},
                ]
            },
            {
                'label': 'Asitencia',
                'url': 'seleccionar_curso',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Tomar Asistencia', 'url': 'seleccionar_curso'},
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},                    
                ]
            },
            {
                'label': 'Informes',
                'url': 'menu_informes',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Informe Notas x Asignatura', 'url': 'seleccionar_parametros_informe'},
                    {'name': 'Informe Notas x Alumnos', 'url': 'seleccionar_parametros_informe_alumno'},
                    {'name': 'Certificado Alumno Regular', 'url': 'certificado_form'},
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},
                ]
            }         
                 
        ],
        
        
        'SECRETARIA': [
            {
                'label': 'Horario de Clases',
                'url': 'horario_lista',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Listar Horarios', 'url': 'horario_lista'},
                    {'name': 'Crear Horaio', 'url': 'horario_crear'},
                ]
            },
            {
                'label': 'Pago Escolaridad',
                'url': 'lista_pagos_mensualidad',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Listar Pagos', 'url': 'lista_pagos_mensualidad'},
                    {'name': 'Crear Pagos', 'url': 'crear_pago_mensualidad'},
                ]
            },
            {
                'label': 'Informes',
                'url': 'menu_informes',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Informe Notas x Asignatura', 'url': 'seleccionar_parametros_informe'},
                    {'name': 'Informe Notas x Alumnos', 'url': 'seleccionar_parametros_informe_alumno'},
                    {'name': 'Certificado Alumno Regular', 'url': 'certificado_form'},
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},
                    
                ]
            }       
            
        ],
        # ... otros roles
    }
    
    # Obtener el menú correspondiente al rol del usuario
    rol = request.user.rol
    menu = menus.get(rol, [])
    
    context = {
        # Datos estadísticos
        'total_usuarios': total_usuarios,
        'total_cursos': total_cursos,
        'total_matriculas': total_matriculas,
        
        
        #datos del menu
        'menu': menu,
        # ... resto del contexto
    }
    
    
    return render(request, "colegio/dashboard.html", context)

#funciones de usuarios

def lista_usuarios(request):
    """Vista para listar usuarios"""
    usuarios = Usuario.objects.all()  # Obtén todos los usuarios
    return render(request, 'colegio/lista_usuarios.html', {'usuarios': usuarios})


@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('lista_usuarios')
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = UsuarioForm()

    return render(request, 'colegio/crear_usuario.html', {'form': form})


@login_required
def detalle_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'detalle_usuario.html', {'usuario': usuario})


@login_required
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('lista_usuarios')
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'colegio/editar_usuario.html', {'form': form})


@login_required
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, "Usuario  eliminado exitosamente.")
        return redirect('lista_usuarios')       
    return render(request, 'confirmar_eliminar.html', {'usuario': usuario})


#funciones de Sedes

@login_required
def lista_sedes(request):
    sedes = Sede.objects.all()
    return render(request, 'colegio/lista_sedes.html', {'sedes': sedes})

@login_required
def crear_sede(request):
    if request.method == 'POST':
        form = SedeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_sedes')
    else:
        form = SedeForm()
    return render(request, 'colegio/formulario_sede.html', {'form': form})

@login_required
def editar_sede(request, pk):
    sede = get_object_or_404(Sede, pk=pk)
    if request.method == 'POST':
        form = SedeForm(request.POST, instance=sede)
        if form.is_valid():
            form.save()
            return redirect('lista_sedes')
    else:
        form = SedeForm(instance=sede)
    return render(request, 'colegio/formulario_sede.html', {'form': form})

@login_required
def eliminar_sede(request, pk):
    sede = get_object_or_404(Sede, pk=pk)
    if request.method == 'POST':
        sede.delete()
        return redirect('lista_sedes')
    return render(request, 'colegio/confirmar_eliminar_sede.html', {'sede': sede})


#Vista Cursos

@login_required
def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'colegio/lista_cursos.html', {'cursos': cursos})

@login_required
def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, pk=curso_id)
    return render(request, 'colegio/detalle_curso.html', {'curso': curso})

@login_required
def crear_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso creado exitosamente.')
            return redirect('lista_cursos')
    else:
        form = CursoForm()
    return render(request, 'colegio/crear_curso.html', {'form': form})

@login_required
def editar_curso(request, curso_id):
    curso = get_object_or_404(Curso, pk=curso_id)
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso actualizado exitosamente.')
            return redirect('lista_cursos')
    else:
        form = CursoForm(instance=curso)
    return render(request, 'colegio/editar_curso.html', {'form': form, 'curso': curso})

@login_required
def eliminar_curso(request, curso_id):
    curso = get_object_or_404(Curso, pk=curso_id)
    if request.method == 'POST':
        curso.delete()
        messages.success(request, 'Curso eliminado exitosamente.')
        return redirect('lista_cursos')
    return render(request, 'colegio/eliminar_curso.html', {'curso': curso})


#vistas asignaturas.


@login_required
def lista_asignaturas(request):
    asignaturas = Asignatura.objects.all().order_by("-id")
    return render(request, 'colegio/lista_asignaturas.html', {
        'asignaturas': asignaturas
    })

@login_required
def detalle_asignatura(request, pk):
    asignatura = get_object_or_404(Asignatura, pk=pk)
    return render(request, 'colegio/detalle_asignatura.html', {
        'asignatura': asignatura
    })


@login_required
def crear_asignatura(request):
    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            form.save()  # Simplemente guarda sin asignar
            messages.success(request, 'Asignatura creada exitosamente.')
            return redirect('lista_asignaturas')
    else:
        form = AsignaturaForm()
    return render(request, 'colegio/crear_asignatura.html', {
        'form': form
    })

@login_required
def editar_asignatura(request, pk):
    asignatura = get_object_or_404(Asignatura, pk=pk)
    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asignatura actualizada exitosamente.')
            return redirect('lista_asignaturas')
    else:
        form = AsignaturaForm(instance=asignatura)
    return render(request, 'colegio/editar_asignatura.html', {
        'form': form,
        'asignatura': asignatura
    })

@login_required
def eliminar_asignatura(request, pk):
    asignatura = get_object_or_404(Asignatura, pk=pk)
    if request.method == 'POST':
        asignatura.delete()
        messages.success(request, 'Asignatura eliminada exitosamente.')
        return redirect('lista_asignaturas')
    return render(request, 'colegio/eliminar_asignatura.html', {
        'asignatura': asignatura
    })
    
#dias de la semana

class DiaSemanaListView(ListView):
    model = DiaSemana
    template_name = 'colegio/lista_dias.html'
    context_object_name = 'dias'

class DiaSemanaCreateView(CreateView):
    model = DiaSemana
    form_class = DiaSemanaForm
    template_name = 'colegio/crear_dia.html'
    success_url = reverse_lazy('lista_dias')

class DiaSemanaUpdateView(UpdateView):
    model = DiaSemana
    form_class = DiaSemanaForm
    template_name = 'colegio/editar_dia.html'
    success_url = reverse_lazy('lista_dias')

class DiaSemanaDeleteView(DeleteView):
    model = DiaSemana
    template_name = 'colegio/confirmar_eliminar_dia.html'
    success_url = reverse_lazy('lista_dias')    
    

#vistas Matriculas


class MatriculaCreateView(LoginRequiredMixin, CreateView):
    model = Matricula
    form_class = MatriculaForm
    template_name = 'colegio/crear_matricula.html'
    success_url = reverse_lazy('lista_matriculas')

    def form_valid(self, form):
        # Asigna el usuario autenticado al campo usuario_creacion
        form.instance.usuario_creacion = self.request.user
        
        try:
            # Intenta guardar el formulario
            response = super().form_valid(form)
            messages.success(self.request, 'Matrícula creada exitosamente.')
            return response
        except ValidationError as e:
            # Maneja cualquier error de validación
            form.add_error(None, e)
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Añade un mensaje de error general
        messages.error(self.request, 'Hubo un error al crear la matrícula. Por favor, revise los campos.')
        return super().form_invalid(form)

class MatriculaUpdateView(LoginRequiredMixin, UpdateView):
    model = Matricula
    form_class = MatriculaForm
    template_name = 'colegio/editar_matricula.html'
    success_url = reverse_lazy('lista_matriculas')

    def form_valid(self, form):
        # Asigna el usuario autenticado al campo usuario_modificacion
        form.instance.usuario_modificacion = self.request.user
        
        try:
            # Intenta guardar el formulario
            response = super().form_valid(form)
            messages.success(self.request, 'Matrícula actualizada exitosamente.')
            return response
        except ValidationError as e:
            # Maneja cualquier error de validación
            form.add_error(None, e)
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Añade un mensaje de error general
        messages.error(self.request, 'Hubo un error al actualizar la matrícula. Por favor, revise los campos.')
        return super().form_invalid(form)

class MatriculaListView(LoginRequiredMixin, ListView):
    model = Matricula
    template_name = 'colegio/lista_matriculas.html'
    context_object_name = 'matriculas'
    
    def get_queryset(self):
        # Puedes añadir filtros si es necesario
        return Matricula.objects.all().order_by('-año', 'alumno')


class MatriculaDetailView(LoginRequiredMixin, DetailView):
    model = Matricula
    template_name = 'colegio/detalle_matricula.html'
    context_object_name = 'matricula'
    

class MatriculaDeleteView(LoginRequiredMixin, DeleteView):
    model = Matricula
    template_name = 'colegio/confirmar_eliminar_matricula.html'
    success_url = reverse_lazy('lista_matriculas')
    
#vistas asigana profesor a sede



class AsignacionListView(ListView):
    model = AsignacionProfesorSede
    template_name = 'colegio/asignacion_list.html'
    context_object_name = 'asignaciones'

class AsignacionCreateView(CreateView):
    model = AsignacionProfesorSede
    form_class = AsignacionForm
    template_name = 'colegio/crea_asignacionprofe.html'
    success_url = reverse_lazy('asignacion_list') #Redirige a la lista después de crear

class AsignacionUpdateView(UpdateView):
    model = AsignacionProfesorSede
    form_class = AsignacionForm
    template_name = 'colegio/crea_asignacionprofe.html'
    success_url = reverse_lazy('asignacion_list')#Redirige a la lista después de actualizar

class AsignacionDeleteView(DeleteView):
    model = AsignacionProfesorSede
    template_name = 'colegio/elimina_asignacionprofe.html'
    success_url = reverse_lazy('asignacion_list')#Redirige a la lista después de eliminar 
    

#calificaciones
@login_required
def lista_calificaciones(request):
    # Primero obtenemos las asignaturas del profesor
    asignaturas_profesor = Asignatura.objects.filter(profesor=request.user)
    
    # Luego obtenemos las calificaciones solo de esas asignaturas
    calificaciones = Calificacion.objects.filter(
        asignatura__in=asignaturas_profesor
    ).select_related(
        'matricula__alumno', 
        'asignatura',
        'matricula__curso'
    ).order_by(
        'asignatura__nombre',
        'matricula__curso',
        'matricula__alumno__last_name',
        'matricula__alumno__first_name',
        '-semestre',
        'tipo'
    )
    
    # Agrupamos las calificaciones por asignatura y curso para mejor organización
    calificaciones_agrupadas = {}
    for calificacion in calificaciones:
        key = (calificacion.asignatura.nombre, calificacion.matricula.curso)
        if key not in calificaciones_agrupadas:
            calificaciones_agrupadas[key] = []
        calificaciones_agrupadas[key].append(calificacion)
    
    return render(request, 'colegio/lista_calificaciones.html', {
        'calificaciones_agrupadas': calificaciones_agrupadas
    })
    

@login_required
def eliminar_calificacion(request, calificacion_id):
    calificacion = get_object_or_404(Calificacion, id=calificacion_id, profesor=request.user)
    
    if request.method == 'POST':
        calificacion.delete()
        return redirect('lista_calificaciones')
    
    return render(request, 'colegio/eliminar_calificacion.html', {
        'calificacion': calificacion
    })



@login_required
def horario_lista(request):
    # Consulta base de horarios
    horarios = Horario.objects.all()
    
    # Formulario de filtros
    form_filtro = HorarioFiltroForm(request.GET)
    
    # Aplicar filtros si son válidos
    if form_filtro.is_valid():
        curso = form_filtro.cleaned_data.get('curso')
        asignatura = form_filtro.cleaned_data.get('asignatura')
        profesor = form_filtro.cleaned_data.get('profesor')
        
        # Filtrar por cada campo si está presente
        if curso:
            horarios = horarios.filter(curso=curso)
        if asignatura:
            horarios = horarios.filter(asignatura=asignatura)
        if profesor:
            horarios = horarios.filter(asignacion_profesor_sede__usuario=profesor)
    
    # Incluir contexto de filtros y horarios
    context = {
        'horarios': horarios,
        'form_filtro': form_filtro
    }
    return render(request, 'colegio/horario_lista.html', context)

@login_required
def horario_crear(request):
    if request.method == 'POST':
        form = HorarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Horario creado exitosamente')
            return redirect('horario_lista')
    else:
        form = HorarioForm()
    
    return render(request, 'colegio/horario_form.html', {'form': form})

@login_required
def horario_editar(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    
    if request.method == 'POST':
        form = HorarioForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Horario actualizado exitosamente')
            return redirect('horario_lista')
    else:
        form = HorarioForm(instance=horario)
    
    return render(request, 'colegio/horario_form.html', {'form': form})

@login_required
def horario_eliminar(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    
    if request.method == 'POST':
        horario.delete()
        messages.success(request, 'Horario eliminado exitosamente')
        return redirect('horario_lista')
    
    return render(request, 'colegio/horario_confirmar_eliminar.html', {'horario': horario})



@login_required
def lista_pagos_mensualidad(request):
    # Obtiene todos los pagos con las relaciones necesarias
    pagos = PagoMensualidad.objects.all().select_related('matricula__alumno')

    # Inicializa el formulario con los datos de la solicitud GET
    form_filtro = PagoMensualidadFiltroForm(request.GET)

    # Verifica si el formulario es válido
    if form_filtro.is_valid():
        # Obtiene los datos filtrados
        alumno = form_filtro.cleaned_data.get('alumno')
        año = form_filtro.cleaned_data.get('año')
        mes = form_filtro.cleaned_data.get('mes')
        estado = form_filtro.cleaned_data.get('estado')

        # Aplica los filtros al queryset
        if alumno:
            pagos = pagos.filter(matricula=alumno)
        if año:
            pagos = pagos.filter(año=año)
        if mes:
            pagos = pagos.filter(mes=mes)
        if estado:
            pagos = pagos.filter(estado=estado)

    # Contexto para la plantilla
    context = {
        'pagos': pagos,
        'form_filtro': form_filtro
    }
    return render(request, 'colegio/lista_pagos.html', context)


@login_required
def crear_pago_mensualidad(request):
    if request.method == 'POST':
        form = PagoMensualidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pago de mensualidad registrado exitosamente.')
            return redirect('lista_pagos_mensualidad')
        else:
            messages.success(request, 'ya se encuntra realizado un pago en este mes y año.')
    else:
        form = PagoMensualidadForm()
    
    return render(request, 'colegio/form_pago.html', {'form': form})

@login_required
def editar_pago_mensualidad(request, pk):
    pago = get_object_or_404(PagoMensualidad, pk=pk)
    
    if request.method == 'POST':
        form = PagoMensualidadForm(request.POST, instance=pago)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pago de mensualidad actualizado exitosamente.')
            return redirect('lista_pagos_mensualidad')
    else:
        form = PagoMensualidadForm(instance=pago)
    
    return render(request, 'colegio/form_pago.html', {'form': form})

@login_required
def eliminar_pago_mensualidad(request, pk):
    pago = get_object_or_404(PagoMensualidad, pk=pk)
    
    if request.method == 'POST':
        pago.delete()
        messages.success(request, 'Pago de mensualidad eliminado exitosamente.')
        return redirect('lista_pagos_mensualidad')
    
    return render(request, 'colegio/eliminar_pago.html', {'pago': pago})



def generar_voucher_pdf(request, pago_id):
    pago = get_object_or_404(PagoMensualidad, id=pago_id)
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    # Ruta para guardar temporalmente el PDF
    #pdf_path = os.path.join(settings.MEDIA_ROOT, f"vouchers/voucher_{pago.id}.pdf")
    pdf_path = str(settings.MEDIA_ROOT / 'vouchers' / f'voucher_{pago.id}.pdf')
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    # Crear el PDF con ReportLab
    c = canvas.Canvas(pdf_path, pagesize=letter)  # Asegúrate de que el tamaño sea carta
    
    # Título en negrita y tamaño 18
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Pago de Mensualidad Colegio más que Vencedores")

    
    # Dejar espacio en blanco (aquí, 20 unidades por ejemplo)   
    espacio = 30
    # Espacio y el resto de texto
    c.setFont("Helvetica", 12)
    c.drawString(50, 730 - espacio, f"Alumno: {pago.matricula.alumno.get_full_name()}")
    c.drawString(50, 710 - espacio, f"Mes: {pago.get_mes_display()}")
    c.drawString(50, 690 - espacio, f"Año: {pago.año}")
    c.drawString(50, 670 - espacio, f"Monto: ${pago.monto}")
    c.drawString(50, 650 - espacio, f"Fecha de Pago: {pago.fecha_pago or 'Pendiente'}")
    c.drawString(50, 630 - espacio, f"Estado: {pago.get_estado_display()}")
    c.drawString(50, 610 - espacio, f"Generado el: {now().strftime('%d/%m/%Y')}")
    print(f"PDF Path completo: {pdf_path}")
    print(f"Directorio existe?: {os.path.exists(os.path.dirname(pdf_path))}")
    c.showPage()
    c.save()
    print(f"PDF creado?: {os.path.exists(pdf_path)}")
    print(f"Permisos carpeta: {os.access(os.path.dirname(pdf_path), os.W_OK)}")
        
    # Preparar el enlace para WhatsApp
    mensaje = f"Hola, este es tu comprobante de pago de mensualidad:\n" \
              f"Colegio mas que vencedores:\n" \
              f"Alumno: {pago.matricula.alumno.get_full_name()}\n" \
              f"Mes: {pago.get_mes_display()} Año: {pago.año}\n" \
              f"Monto: ${pago.monto}\n" \
              f"Estado: {pago.get_estado_display()}\n" \
              f"Fecha de Pago: {pago.fecha_pago or 'Pendiente'}"
    whatsapp_url = f"https://wa.me/?{urlencode({'text': mensaje})}"
    
    # Enviar el archivo PDF en la respuesta o permitir compartirlo
    return render(request, 'colegio/voucher_detalle.html', {
        'pago': pago,
        #'pdf_url': f"{settings.MEDIA_URL}vouchers/voucher_{pago.id}.pdf",
        'pdf_url': f'/media/vouchers/voucher_{pago.id}.pdf',  # URL siempre con forward slashes
        'whatsapp_url': whatsapp_url,
    })
    
#ASITENCIA
@login_required
def seleccionar_curso(request):
    if request.method == 'POST':
        form = AsistenciaSeleccionForm(request.POST, usuario=request.user)
        if form.is_valid():
            request.session['asignatura_id'] = form.cleaned_data['asignatura'].id
            return redirect('tomar_asistencia')
    else:
        form = AsistenciaSeleccionForm(usuario=request.user)
    
    return render(request, 'colegio/seleccionar_curso.html', {'form': form})


@login_required
def tomar_asistencia(request):
    asignatura_id = request.session.get('asignatura_id')
    if not asignatura_id:
        return redirect('seleccionar_curso')
    
    asignatura = Asignatura.objects.get(id=asignatura_id)
    matriculas = Matricula.objects.filter(curso=asignatura.curso)
    
    if request.method == 'POST':
        formset = RegistroAsistenciaFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    registro = form.save(commit=False)
                    registro.asignatura = asignatura
                    registro.fecha_hora = timezone.now()
                    registro.save()
            messages.success(request, 'Asistencia registrada correctamente')
            return redirect('dashboard')
    else:
        initial = [{'matricula': matricula.id} for matricula in matriculas]
        formset = RegistroAsistenciaFormSet(initial=initial)
    
    return render(request, 'colegio/tomar_asistencia.html', {
        'formset': formset,
        'asignatura': asignatura
    })

#CALIFICACIONES
# Decorador que asegura que el usuario esté autenticado para acceder a esta vista
@login_required
def seleccionar_curso_calificacion(request):
    # Si la solicitud es POST (el usuario envió el formulario)
    if request.method == 'POST':
        # Creamos un formulario con los datos enviados y pasamos el usuario actual
        form = CalificacionSeleccionForm(request.POST, usuario=request.user)
        # Validamos el formulario
        if form.is_valid():
            # Guardamos en la sesión los datos seleccionados en el formulario
            request.session['calificacion_asignatura_id'] = form.cleaned_data['asignatura'].id
            request.session['calificacion_tipo'] = form.cleaned_data['tipo']
            request.session['calificacion_semestre'] = form.cleaned_data['semestre']
            request.session['calificacion_especificacion'] = form.cleaned_data.get('especificacion', None)

            # Redirigimos al usuario a la vista de ingreso de calificaciones
            return redirect('ingresar_calificaciones')
    else:
        # Si la solicitud es GET (el usuario accede por primera vez), creamos un formulario vacío
        form = CalificacionSeleccionForm(usuario=request.user)
    
    # Renderizamos la plantilla con el formulario para que el usuario lo complete
    return render(request, 'colegio/seleccionar_curso_calificacion.html', {'form': form})


@login_required
def ingresar_calificaciones(request):
    # Recuperamos los datos seleccionados en la vista anterior
    asignatura_id = request.session.get('calificacion_asignatura_id')
    tipo = request.session.get('calificacion_tipo')
    semestre = request.session.get('calificacion_semestre')
    especificacion = request.session.get('calificacion_especificacion')

    if not all([asignatura_id, tipo, semestre]):  # Quitamos la validación estricta de especificación
        return redirect('seleccionar_curso_calificacion')
    
    asignatura = Asignatura.objects.get(id=asignatura_id)
    matriculas = Matricula.objects.filter(
        curso=asignatura.curso,
        estado='ACTIVO'
    ).select_related('alumno').order_by('alumno__last_name', 'alumno__first_name')

    # Ignorar la especificación al buscar las calificaciones
    calificaciones = Calificacion.objects.filter(
        asignatura=asignatura,
        tipo=tipo,
        semestre=semestre
    )

    if request.method == 'POST':
        formset = CalificacionFormSet(request.POST, queryset=calificaciones)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.asignatura = asignatura
                instance.profesor = request.user
                instance.tipo = tipo
                instance.semestre = semestre
                # Sigue guardando la especificación si existe
                instance.especificacion = especificacion
                instance.save()
            messages.success(request, 'Calificaciones guardadas correctamente')
            return redirect('dashboard')
    else:
        # Crear calificaciones por defecto si no existen
        if not calificaciones.exists():
            for matricula in matriculas:
                Calificacion.objects.get_or_create(
                    matricula=matricula,
                    asignatura=asignatura,
                    profesor=request.user,
                    tipo=tipo,
                    semestre=semestre,
                    # Especificación aún puede ser asignada al crear
                    defaults={'nota': 1.0, 'especificacion': especificacion}
                )
            calificaciones = Calificacion.objects.filter(
                asignatura=asignatura,
                tipo=tipo,
                semestre=semestre
            ).order_by('matricula__alumno__last_name', 'matricula__alumno__first_name')
        
        formset = CalificacionFormSet(queryset=calificaciones)
    
    # Asociar formularios con nombres de estudiantes
    alumnos_forms = []
    for form in formset:
        nombre_completo = f"{form.instance.matricula.alumno.last_name} {form.instance.matricula.alumno.first_name}"
        alumnos_forms.append((form, nombre_completo))
    
    return render(request, 'colegio/ingresar_calificaciones.html', {
        'formset': formset,
        'alumnos_forms': alumnos_forms,
        'asignatura': asignatura,
        'tipo': dict(Calificacion.TIPO_CHOICES)[tipo],
        'semestre': f"{semestre}° Semestre",
        'especificacion': especificacion  # Sigue siendo visible pero no afecta la búsqueda
    })


# vistas de informes de notas

def es_profesor(user):
    return user.rol == 'PROFESOR'

@login_required
@user_passes_test(es_profesor)
def seleccionar_parametros_informe(request):
    if request.method == 'POST':
        form = ParametrosInformeForm(request.user, request.POST)
        if form.is_valid():
            asignatura_id = form.cleaned_data['asignatura'].id
            año = form.cleaned_data['año']
            semestre = form.cleaned_data['semestre']
            return redirect('generar_informe_notas', asignatura_id=asignatura_id, año=año, semestre=semestre)
    else:
        form = ParametrosInformeForm(request.user)
    
    return render(request, 'colegio/seleccionar_parametros.html', {
        'form': form
    })


def seleccionar_parametros_informe(request):
    if request.method == 'POST':
        form = ParametrosInformeForm(request.user, request.POST)
        if form.is_valid():           
            asignatura_id = form.cleaned_data['asignatura'].id
            año = form.cleaned_data['año']
            semestre = form.cleaned_data['semestre']
            return redirect(
                'generar_informe_notas',               
                asignatura_id=asignatura_id,
                año=año,
                semestre=semestre
            )
    else:
        form = ParametrosInformeForm(request.user)
    
    return render(request, 'colegio/seleccionar_parametros.html', {
        'form': form
    })



@login_required
@user_passes_test(es_profesor)
def generar_informe_notas(request, asignatura_id, año, semestre):
    # Verificar que la asignatura existe y el profesor tiene acceso
    
    asignatura = get_object_or_404(Asignatura, id=asignatura_id, profesor=request.user)
    
    # Obtener calificaciones
    calificaciones = Calificacion.objects.filter(
        profesor=request.user,
        asignatura=asignatura,
        semestre=semestre
    ).order_by('matricula__alumno__last_name', 
               'matricula__alumno__first_name', 
               'tipo')
        
    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=1,
        spaceAfter=30
    )
    
    # Título
    title = Paragraph(
        f"INFORME DE NOTAS - {asignatura.curso.nombre} - {asignatura.nombre}",
        title_style
    )
    elements.append(title)
    
    # Subtítulo con información adicional
    subtitle = Paragraph(
        f"Año: {año} - Semestre: {semestre}",
        styles['Normal']
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # Preparar datos para la tabla
    data = [['Alumno', 'Nota 1', 'Nota 2', 'Nota 3', 'Nota 4', 'Nota 5', 'Promedio']]
    
    # Agrupar calificaciones por alumno
    alumnos_data = {}
    for calif in calificaciones:
        alumno = calif.matricula.alumno
        if alumno not in alumnos_data:
            alumnos_data[alumno] = {'notas': {}, 'promedio': 0}
        alumnos_data[alumno]['notas'][calif.tipo] = calif.nota
    
    # Calcular promedios y llenar la tabla
    for alumno, datos in alumnos_data.items():
        notas = []
        suma = Decimal('0')
        count = 0
        for tipo in ['NOTA 1', 'NOTA 2', 'NOTA 3', 'NOTA 4', 'NOTA 5']:
            nota = datos['notas'].get(tipo, '')
            notas.append(str(nota) if nota else '-')
            if nota:
                suma += Decimal(str(nota))
                count += 1
        
        promedio = round(suma / count, 2) if count > 0 else '-'
        data.append([
            f"{alumno.last_name}, {alumno.first_name}",
            *notas,
            str(promedio)
        ])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ]))
    
    elements.append(table)
    
    # Agregar firma del profesor
    elements.append(Spacer(1, 50))
    firma = Paragraph(f"""
    <para alignment="center">
    _______________________<br/>
    {request.user.get_full_name()}<br/>
    Profesor
    </para>
    """, styles['Normal'])
    elements.append(firma)
    
    # Generar PDF
    doc.build(elements)
    
    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"informe_notas_{asignatura.curso.nombre}_{asignatura.nombre}_S{semestre}_{año}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response



#informe de notas x alumnos

@login_required
@user_passes_test(es_profesor)
def seleccionar_parametros_informe_alumno(request):
    if request.method == 'POST':
        form = ParametrosInformeAlumnoForm(request.POST)
        if form.is_valid():
            matricula = form.cleaned_data['alumno']
            alumno_id = matricula.alumno.id
            año = form.cleaned_data['año']
            semestre = form.cleaned_data['semestre']
            return redirect('generar_informe_notas_alumno', 
                          alumno_id=alumno_id, 
                          año=año, 
                          semestre=semestre)
    else:
        form = ParametrosInformeAlumnoForm()
    
    return render(request, 'colegio/seleccionar_parametros_alumno.html', {
        'form': form
    })

def load_alumnos_notas(request):
    curso_id = request.GET.get('curso')
    matriculas = Matricula.objects.filter(
        curso_id=curso_id,
        estado='ACTIVO'
    ).select_related('alumno')
    return JsonResponse(
        list(matriculas.values('id', 'alumno__first_name', 'alumno__last_name')), 
        safe=False
    )    
    
    
    
@login_required
def generar_informe_notas_alumno(request, alumno_id, año, semestre):
    # Obtener el alumno
    alumno = get_object_or_404(Usuario, id=alumno_id, rol='ALUMNO')
    
    # Obtener el curso del alumno a través de su matrícula
    matricula = Matricula.objects.filter(alumno=alumno, año=año).first()
    curso = matricula.curso if matricula else None
    
    # Obtener todas las calificaciones del alumno para el semestre y año especificados
    calificaciones = Calificacion.objects.filter(
        matricula__alumno=alumno,
        semestre=semestre
    ).order_by('asignatura__nombre', 'tipo')
    
    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=1,
        spaceAfter=30
    )
    
    # Título
    title = Paragraph(
        f"INFORME DE NOTAS - COLEGIO MAS QUE VENCEDORES",       
        title_style
    )
    elements.append(title)
    
    # Información del alumno
    profesor_jefe = curso.profesor_jefe.get_full_name() if curso and curso.profesor_jefe else "No asignado"
    nivel = curso.get_nivel_display() if curso else "No especificado"
    curso_nombre = curso.nombre if curso else "No especificado"

    curso_año = curso.año if curso else "No especificado"
    
    alumno_info_style = ParagraphStyle(
        'AlumnoInfoStyle',
        parent=styles['Normal'],  # Basado en el estilo 'Normal'
        fontSize=11,  # Tamaño de fuente (puedes ajustarlo a lo que prefieras)
        leading=14,  # Interlineado (ajusta según lo necesario)
    )
    alumno_info = Paragraph(
        f"""
        <b>Alumno:</b> {alumno.get_full_name()}<br/>
        <b>Profesor Jefe:</b> {profesor_jefe}<br/>
        <b>Curso:</b> {curso_nombre}<br/>
        <b>Semestre N°:</b> {semestre}<br/>
        <b>Tipo de Enseñanza:</b> {nivel}<br/>
        <b>Año:</b> {curso_año}
        """,
        alumno_info_style  # Aplicar el estilo personalizado
    )
    elements.append(alumno_info)
    
    # Espaciado
    elements.append(Paragraph("<br/><br/>", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Preparar datos para la tabla
    data = [['Asignatura', 'Nota 1', 'Nota 2', 'Nota 3', 'Nota 4', 'Nota 5', 'Promedio']]
    
    # Agrupar calificaciones por asignatura
    asignaturas_data = {}
    for calif in calificaciones:
        asignatura = calif.asignatura
        if asignatura not in asignaturas_data:
            asignaturas_data[asignatura] = {'notas': {}, 'promedio': 0}
        asignaturas_data[asignatura]['notas'][calif.tipo] = calif.nota
    
    # Calcular promedios y llenar la tabla
    promedio_general = Decimal('0')
    asignaturas_con_notas = 0
    
    for asignatura, datos in asignaturas_data.items():
        notas = []
        suma = Decimal('0')
        count = 0
        for tipo in ['NOTA 1', 'NOTA 2', 'NOTA 3', 'NOTA 4', 'NOTA 5']:
            nota = datos['notas'].get(tipo, '')
            notas.append(str(nota) if nota else '-')
            if nota:
                suma += Decimal(str(nota))
                count += 1
        
        if count > 0:
            promedio = round(suma / count, 2)
            promedio_general += promedio
            asignaturas_con_notas += 1
        else:
            promedio = '-'
            
        data.append([
            asignatura.nombre,
            *notas,
            str(promedio) if promedio != '-' else '-'
        ])
    
    # Calcular promedio general
    if asignaturas_con_notas > 0:
        promedio_general = round(promedio_general / asignaturas_con_notas, 2)
        data.append(['Promedio General', '', '', '', '', '', str(promedio_general)])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        # Estilo especial para la fila del promedio general
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    
    # Agregar firma del profesor
    elements.append(Spacer(1, 50))
    firma = Paragraph(f"""
    <para alignment="center">
    _______________________<br/>
    {profesor_jefe}<br/>
    Profesor Jefe
    </para>
    """, styles['Normal'])
    elements.append(firma)
    
    # Generar PDF
    doc.build(elements)
    
    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"informe_notas_{alumno.get_full_name()}_S{semestre}_{año}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

#CERTIFICADO ALUMNO REGULAR
class CertificadoView(FormView):
    template_name = 'colegio/certificado_form.html'
    form_class = CertificadoForm
    success_url = reverse_lazy('certificado_form')

    def form_valid(self, form):
        matricula = form.cleaned_data['alumno']
        semestre = form.cleaned_data['semestre']
        
        # Configuración de la respuesta HTTP para PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="certificado.pdf"'

        # Crear el PDF
        p = canvas.Canvas(response)
        
        # Título del certificado
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(300, 770, "CERTIFICADO DE ALUMNO REGULAR")
        #p.drawCentredString(300, 770, "COLEGIO MAS QUE VENCEDORES")

        # Cuerpo del certificado
        p.setFont("Helvetica", 12)
        p.drawString(50, 700, "     JESSICA GUERRA, Directora Colegio más que Vencedores Sede Colín. Región del Maule.")
        p.drawString(50, 680, f"Certifica que {matricula.alumno}, RUN N° {matricula.alumno.rut}, es alumno(a) regular")
        p.drawString(50, 660, f"de {matricula.curso.nombre} durante el período académico {matricula.año}.")
        
        p.drawString(50, 620, "Se extiende el presente certificado a petición del interesado(a) para: FINES QUE")
        p.drawString(50, 600, "ESTIME CONVENIENTES.")
        
       

        # Firma
        p.drawString(300, 450, "________________________")
        p.drawString(300, 430, "Jessica Guerra")
        p.drawString(300, 410, "Directora MQV")
         # Fecha
        p.drawString(50, 360, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")

        # Validez
        p.drawString(50, 340, "Válido por 60 días.")
        p.drawString(50,50, "Departamento de Admisión y Registro Académico MQV.")
        p.drawString(50, 30, "Av. Colin S/N - Maule, Fono: 71-22464564 admision@mqv.cl")
        
        
        # Finalizar el PDF
        p.showPage()
        p.save()

        return response


#carga alumnos
def load_alumnos(request):
    curso_id = request.GET.get('curso')
    alumnos = Matricula.objects.filter(
        curso_id=curso_id,
        estado='ACTIVO'
    ).select_related('alumno')
    return JsonResponse(
        list(alumnos.values('id', 'alumno__first_name', 'alumno__last_name')), 
        safe=False
    )

# genera informe de asistencia 

def exportar_excel(context):
    # Crear un nuevo libro de trabajo
    wb = Workbook()
    ws = wb.active
    
    # Configurar el título
    ws.merge_cells('A1:D1')
    ws['A1'] = 'Informe de Asistencia'
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = Alignment(horizontal='left')
    
    # Configurar el subtítulo
    ws.merge_cells('A2:D2')
    ws['A2'] = f"Asignatura: {context['asignatura']}, Año: {context['anio']}, Mes: {context['nombre_mes']}"
    ws['A2'].font = Font(bold=True)
    ws['A2'].alignment = Alignment(horizontal='left')
    
    # Configurar encabezados
    headers = ['Alumno']
    fechas = context['fechas']
    for fecha in fechas:
        headers.append(str(fecha.day))
    headers.append('% Asistencia')
    
    # Escribir encabezados
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
        if col > 1 and col < len(headers):  # Solo para las fechas
            ws.column_dimensions[get_column_letter(col)].width = 4
    
    # Configurar ancho de columnas específicas
    ws.column_dimensions['A'].width = 30  # Columna de nombres
    ws.column_dimensions[get_column_letter(len(headers))].width = 12  # Columna de porcentaje
    
    # Escribir datos de asistencia
    row = 5
    for alumno, asistencias in context['alumnos_asistencia'].items():
        # Nombre del alumno
        ws.cell(row=row, column=1).value = f"{alumno.last_name}, {alumno.first_name}"
        
        # Estados de asistencia
        for col, fecha in enumerate(fechas, 2):
            cell = ws.cell(row=row, column=col)
            estado = asistencias[fecha]
            cell.value = estado
            cell.alignment = Alignment(horizontal='center')
            
            # Colorear según el estado
            if estado == 'P':
                cell.fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')  # Verde claro
            elif estado == 'A':
                cell.fill = PatternFill(start_color='FFB6C1', end_color='FFB6C1', fill_type='solid')  # Rojo claro
            elif estado == 'J':
                cell.fill = PatternFill(start_color='FFE4B5', end_color='FFE4B5', fill_type='solid')  # Amarillo claro
        
        # Porcentaje de asistencia
        porcentaje = context['estadisticas'][alumno]
        ws.cell(row=row, column=len(headers)).value = f"{porcentaje}%"
        ws.cell(row=row, column=len(headers)).alignment = Alignment(horizontal='center')
        
        row += 1
    
    # Preparar la respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=informe_asistencia.xlsx'
    
    # Guardar el libro de trabajo
    wb.save(response)
    
    return response
# genera informe de asistencia 
@login_required
def generar_informe(request):
    if request.method == 'POST':
        form = InformeAsistenciaForm(request.POST, usuario=request.user)
        if form.is_valid():
            try:
                asignatura = form.cleaned_data['asignatura']
                año = int(form.cleaned_data['año'])
                mes = int(form.cleaned_data['mes'])
                
                # Obtener fechas del mes (solo días de semana)
                primer_dia = date(año, mes, 1)
                ultimo_dia = date(año, mes, calendar.monthrange(año, mes)[1])
                fechas = [date(año, mes, dia) for dia in range(1, ultimo_dia.day + 1)
                         if date(año, mes, dia).weekday() < 5]
                
                # Obtener registros del mes
                registros = RegistroAsistencia.objects.filter(
                    asignatura=asignatura,
                    fecha_hora__date__range=(primer_dia, ultimo_dia)
                ).select_related('matricula__alumno').order_by(
                    'matricula__alumno__last_name',
                    'fecha_hora__date',
                    'fecha_hora__time'
                )
                
                # Crear diccionario de registros por alumno
                alumnos_dict = {}
                for registro in registros:
                    if registro.matricula.estado == 'ACTIVO':
                        alumno = registro.matricula.alumno
                        fecha = registro.fecha_hora.date()
                        
                        if alumno not in alumnos_dict:
                            alumnos_dict[alumno] = {fecha: [] for fecha in fechas}
                            
                        # Agregar el estado a la lista de estados del día
                        if fecha in alumnos_dict[alumno]:
                            alumnos_dict[alumno][fecha].append(registro.estado[0])
                
                # Consolidar múltiples estados por día
                for alumno in alumnos_dict:
                    for fecha in alumnos_dict[alumno]:
                        estados = alumnos_dict[alumno][fecha]
                        if estados:
                            if 'A' in estados:
                                alumnos_dict[alumno][fecha] = 'A'
                            elif 'P' in estados:
                                alumnos_dict[alumno][fecha] = 'P'
                            elif 'J' in estados:
                                alumnos_dict[alumno][fecha] = 'J'
                        else:
                            alumnos_dict[alumno][fecha] = '-'
                
                # Calcular estadísticas
                estadisticas = {}
                for alumno, asistencias in alumnos_dict.items():
                    presentes = sum(1 for estado in asistencias.values() if estado == 'P')
                    total_dias = len(fechas)
                    porcentaje = round((presentes / total_dias * 100), 1) if total_dias > 0 else 0
                    estadisticas[alumno] = porcentaje
                
                context = {
                    'form': form,
                    'asignatura': asignatura,
                    'anio': año,
                    'mes': mes,
                    'nombre_mes': calendar.month_name[mes],
                    'fechas': fechas,
                    'alumnos_asistencia': alumnos_dict,
                    'estadisticas': estadisticas,
                    'tiene_datos': bool(alumnos_dict)
                }
                
                if 'exportar' in request.POST:
                    return exportar_excel(context)
                    
                return render(request, 'colegio/informe_asistencia.html', context)
                
            except Exception as e:
                return render(request, 'colegio/generar_informeAsistencia.html', {
                    'form': form,
                    'error': f'Error al generar el informe: {str(e)}'
                })
    else:
        form = InformeAsistenciaForm(usuario=request.user)
    
    return render(request, 'colegio/generar_informeAsistencia.html', {'form': form})


