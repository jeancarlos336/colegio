from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario,Bitacora, Sede,Evaluacion, Curso, Asignatura, Anotacion, DiaSemana, Matricula,AsignacionProfesorSede,Calificacion,Horario,PagoMensualidad,RegistroAsistencia,RegistroAsistencia, Asignatura
from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.forms import modelformset_factory,formset_factory
from calendar import month_name


class SedeForm(forms.ModelForm):
    class Meta:
        model = Sede
        fields = ['nombre', 'direccion', 'ciudad', 'region', 'telefono', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'rol', 'rut', 'telefono', 'direccion', 'fecha_nacimiento', 'password1', 'password2']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username



class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'rol', 'rut', 'telefono', 'direccion', 'fecha_nacimiento']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'text', 'placeholder': 'dd-mm-yyyy'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True  # Deshabilitar el campo de usuario

    def clean_username(self):
        # Opcional, para validar que el username no cambie manualmente (aunque está deshabilitado)
        return self.instance.username      

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        
        # Si ya es un objeto date, devolverlo directamente
        if isinstance(fecha, date):
            return fecha
        
        # Si es una cadena, convertirla
        if isinstance(fecha, str):
            try:
                fecha_convertida = datetime.strptime(fecha, "%d-%m-%Y").date()
                return fecha_convertida
            except ValueError:
                raise forms.ValidationError("El formato de la fecha debe ser dd-mm-yyyy.")
        
        # Si no es ninguno de los tipos esperados, lanzar un error
        raise forms.ValidationError("Fecha de nacimiento inválida.")



class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'nivel', 'año', 'sede', 'profesor_jefe']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel': forms.Select(attrs={'class': 'form-control'}),
            'año': forms.NumberInput(attrs={'class': 'form-control'}),
            'sede': forms.Select(attrs={'class': 'form-control'}),
            'profesor_jefe': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios con rol "profesor"
        self.fields['profesor_jefe'].queryset = Usuario.objects.filter(rol='PROFESOR')


class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = ['nombre', 'codigo', 'descripcion', 'sede', 'curso','profesor']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sede': forms.Select(attrs={'class': 'form-control'}),
            'curso': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(AsignaturaForm, self).__init__(*args, **kwargs)
        # Filtrar solo los usuarios con rol 'PROFESOR'
        self.fields['profesor'].queryset = Usuario.objects.filter(rol='PROFESOR')   


class DiaSemanaForm(forms.ModelForm):
    class Meta:
        model = DiaSemana
        fields = ['nombre']
        widgets = {
            'nombre': forms.Select(attrs={'class': 'form-control'})
        }




class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ['alumno', 'curso', 'sede', 'año', 'estado']
        widgets = {
            'alumno': forms.Select(attrs={'class': 'form-control'}),
            'curso': forms.Select(attrs={'class': 'form-control'}),
            'sede': forms.Select(attrs={'class': 'form-control'}),
            'año': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2050}),
            'estado': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios con rol "alumno"
        self.fields['alumno'].queryset = Usuario.objects.filter(rol='ALUMNO')

    def clean(self):
        cleaned_data = super().clean()
        
        # Validación para evitar matrículas duplicadas en el mismo año
        alumno = cleaned_data.get('alumno')
        año = cleaned_data.get('año')
        curso = cleaned_data.get('curso')
        
        if alumno and año and curso:
            # Buscar matrículas existentes para este alumno en el mismo año
            matriculas_existentes = Matricula.objects.filter(
                alumno=alumno, 
                año=año
            )
            
            # Si estamos editando una matrícula existente, excluir la matrícula actual
            if self.instance.pk:
                matriculas_existentes = matriculas_existentes.exclude(pk=self.instance.pk)
            
            # Si ya existe una matrícula para este alumno en este año
            if matriculas_existentes.exists():
                # Obtener el curso existente
                curso_existente = matriculas_existentes.first().curso
                raise ValidationError({
                    'curso': f'El alumno ya está matriculado en el curso {curso_existente} para el año {año}.'
                })
        
        # Validación adicional para evitar matrículas duplicadas exactas
        if alumno and curso and año and cleaned_data.get('sede'):
            existe_matricula = Matricula.objects.filter(
                alumno=alumno,
                curso=curso,
                año=año,
                sede=cleaned_data.get('sede')
            ).exclude(pk=self.instance.pk).exists()
            
            if existe_matricula:
                raise forms.ValidationError("Esta matrícula ya existe")
        
        return cleaned_data
    
#este formulario es para asignar profesores por sede
class AsignacionForm(forms.ModelForm):
    class Meta:
        model = AsignacionProfesorSede
        fields = ['usuario', 'sede', 'dias_trabajados']
        widgets = {
            'dias_trabajados': forms.CheckboxSelectMultiple,  # Para seleccionar múltiples días
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Personalizar labels o agregar clases CSS a los widgets
        self.fields['usuario'].queryset = Usuario.objects.filter(rol='PROFESOR')
        self.fields['usuario'].label = "Profesor"       
        self.fields['sede'].label = "Sede"
        self.fields['dias_trabajados'].label = "Días Trabajados"


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = [
            'asignacion_profesor_sede',
            'curso',
            'asignatura',
            'dia',
            'hora_inicio',
            'hora_fin'
        ]
        labels = {
            'asignacion_profesor_sede': 'Profesor'  # Aquí cambias la etiqueta
        }
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }
        
class HorarioFiltroForm(forms.Form):
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(), 
        required=False, 
        label='Curso'
    )
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.all(), 
        required=False, 
        label='Asignatura'
    )
    profesor = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(rol='PROFESOR'), 
        required=False, 
        label='Profesor'
    )


class PagoMensualidadForm(forms.ModelForm):
    alumno = forms.ModelChoiceField(
        queryset=Matricula.objects.filter(estado='ACTIVO').select_related('alumno'),
        to_field_name='id',
        label='Alumno',
        empty_label='Seleccione un alumno',
        required=True
    )

    class Meta:
        model = PagoMensualidad
        fields = ['alumno', 'mes', 'año', 'monto', 'fecha_pago', 'estado']
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
            'año': forms.NumberInput(attrs={'min': 2000, 'max': timezone.now().year}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizar el campo 'alumno' para mostrar nombre completo y RUT
        self.fields['alumno'].label_from_instance = lambda obj: f"{obj.alumno.get_full_name()} - {obj.alumno.rut}"

    def clean(self):
        cleaned_data = super().clean()
        alumno = cleaned_data.get('alumno')
        mes = cleaned_data.get('mes')
        año = cleaned_data.get('año')

        # Validar si ya existe un pago para este alumno en el mismo mes y año
        if alumno and mes and año:
            matricula = alumno  # La matrícula ya se está seleccionando
            if PagoMensualidad.objects.filter(matricula=matricula, mes=mes, año=año).exists():
                raise ValidationError(
                    f'Ya existe un pago registrado para el alumno "{matricula}" en {mes} de {año}.'
                )
        
        return cleaned_data

    def save(self, commit=True):
        # Sobrescribir el método save para asignar correctamente la matrícula
        instance = super().save(commit=False)
        instance.matricula = self.cleaned_data['alumno']
        
        if commit:
            instance.save()
        return instance

    
class PagoMensualidadFiltroForm(forms.Form):
    
    alumno = forms.ModelChoiceField(
       queryset=Matricula.objects.filter(estado='ACTIVO').select_related('alumno'),
       to_field_name='id',
       label='Alumno',
       empty_label='Seleccione un alumno',
       required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizar el campo de alumno para mostrar nombre completo
        self.fields['alumno'].label_from_instance = lambda obj: f"{obj.alumno.get_full_name()}"  # Utilizando el método get_full_name()
        
    año = forms.IntegerField(
        required=False, 
        min_value=2000, 
        max_value=timezone.now().year,
        widget=forms.NumberInput(attrs={'placeholder': 'Año'})
    )
    mes = forms.ChoiceField(
        choices=[('', 'Todos los meses')] + PagoMensualidad.MESES, 
        required=False
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + PagoMensualidad.estado.field.choices, 
        required=False
    )    
    


class AsistenciaSeleccionForm(forms.Form):
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.none(),
        label='Seleccione la asignatura',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha_hora = forms.DateTimeField(
        label='Fecha y Hora',
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'max': timezone.now().strftime('%Y-%m-%dT%H:%M'),  # Restricción en el HTML
            }
        ),
        initial=timezone.now
    )
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(profesor=usuario)

class RegistroAsistenciaForm(forms.ModelForm):
    class Meta:
        model = RegistroAsistencia
        fields = ['matricula', 'estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['matricula'] = forms.ModelChoiceField(
            queryset=Matricula.objects.filter(estado='ACTIVO').select_related('alumno'),
            to_field_name='id',
            label='Alumno',
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        # Personalizar cómo se muestra el nombre del alumno
        self.fields['matricula'].label_from_instance = lambda obj: f"{obj.alumno.get_full_name()}"

RegistroAsistenciaFormSet = formset_factory(RegistroAsistenciaForm, extra=0)


#CALIFICACIONES POR ASIGNATURA
class CalificacionSeleccionForm(forms.Form):
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.none(),
        label='Seleccione la asignatura',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tipo = forms.ChoiceField(
        choices=Calificacion.TIPO_CHOICES,
        label='Tipo de Evaluación',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    semestre = forms.ChoiceField(
        choices=[(1, 'Primer Semestre'), (2, 'Segundo Semestre')],
        label='Semestre',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    especificacion = forms.CharField(
        label='Especificación',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese detalles adicionales'
        })
    )

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(profesor=usuario)
            

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['matricula', 'nota']
        widgets = {
            'nota': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '1.0',
                'max': '7.0'
            }),
            'matricula': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'matricula' in self.initial:
            self.fields['matricula'].initial = self.initial['matricula']

CalificacionFormSet = forms.modelformset_factory(
    Calificacion,
    form=CalificacionForm,
    extra=0,
    can_delete=False
)
  
#informes de notas x semestre
class ParametrosInformeForm(forms.Form):
    asignatura = forms.ModelChoiceField(
        queryset=None,
        empty_label="Seleccione una asignatura",
        label="Asignatura"
    )
    año = forms.IntegerField(
        min_value=2020,
        max_value=2100,
        label="Año",
        initial=2025
    )
    semestre = forms.ChoiceField(
        choices=[(1, 'Primer Semestre'), (2, 'Segundo Semestre')],
        label="Semestre"
    )
    
    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if usuario.rol == 'DIRECTOR':
            self.fields['asignatura'].queryset = Asignatura.objects.all().distinct().order_by("id")
        elif usuario.rol == 'PROFESOR':
            self.fields['asignatura'].queryset = Asignatura.objects.filter(
                profesor=usuario
            ).distinct().order_by("id")
        else:
            self.fields['asignatura'].queryset = Asignatura.objects.none()
            
class ParametrosInformeAlumnoForm(forms.Form):
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        empty_label="Seleccione un curso",
        label="Curso"
    )
    alumno = forms.ModelChoiceField(
        queryset=Matricula.objects.none(),
        empty_label="Seleccione un alumno",
        label="Alumno"
    )
    año = forms.IntegerField(
        min_value=2020,
        max_value=2100,
        label="Año",
        initial=2025
    )
    semestre = forms.ChoiceField(
        choices=[(1, 'Primer Semestre'), (2, 'Segundo Semestre')],
        label="Semestre"
    )
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label="Observaciones"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'curso' in self.data:
            try:
                curso_id = int(self.data.get('curso'))
                self.fields['alumno'].queryset = Matricula.objects.filter(
                    curso_id=curso_id,
                    estado='ACTIVO'
                ).select_related('alumno')
            except (ValueError, TypeError):
                pass


#CERTIFICADO ALUMNO REGULAR
class CertificadoForm(forms.Form):
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        empty_label="Seleccione un curso"
    )
    alumno = forms.ModelChoiceField(
        queryset=Matricula.objects.none(),
        empty_label="Seleccione un alumno"
    )
    semestre = forms.ChoiceField(choices=[
        (1, 'Primer Semestre'),
        (2, 'Segundo Semestre')
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'curso' in self.data:
            try:
                curso_id = int(self.data.get('curso'))
                self.fields['alumno'].queryset = Matricula.objects.filter(
                    curso_id=curso_id,
                    estado='ACTIVO'
                ).select_related('alumno')
            except (ValueError, TypeError):
                pass


#FORMULARIO DE ASISTENCIA
class InformeAsistenciaForm(forms.Form):
    # Obtener el año actual
    año_actual = timezone.now().year
    
    asignatura = forms.ModelChoiceField(
        queryset=None,  # Se establecerá en __init__
        label="Asignatura",
        empty_label="Seleccione una asignatura",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    año = forms.ChoiceField(
        choices=[(str(y), str(y)) for y in range(año_actual - 1, año_actual + 2)],
        label="Año",
        initial=str(año_actual),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    mes = forms.ChoiceField(
        choices=[
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), 
            ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
            ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Septiembre'),
            ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ],
        label="Mes",
        initial=str(timezone.now().month),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar asignaturas según el usuario
        if usuario:
            if usuario.rol in ['ADMIN', 'DIRECTOR'] or usuario.is_staff:
                # Si es admin o director, mostrar todas las asignaturas
                self.fields['asignatura'].queryset = Asignatura.objects.all().order_by("id")
            elif usuario.rol == 'PROFESOR':
                # Si es profesor, mostrar solo sus asignaturas
                self.fields['asignatura'].queryset = Asignatura.objects.filter(profesor=usuario).order_by("id")
            else:
                # Para otros roles, no mostrar asignaturas (o ajusta según sea necesario)
                self.fields['asignatura'].queryset = Asignatura.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        año = cleaned_data.get('año')
        mes = cleaned_data.get('mes')
        
        if año and mes:
            # Convertir a enteros para validación
            año = int(año)
            mes = int(mes)
            
            # Validar que no sea una fecha futura
            fecha_actual = timezone.now().date()
            if año > fecha_actual.year or (año == fecha_actual.year and mes > fecha_actual.month):
                raise ValidationError("No puede generar informes para fechas futuras")
            
            # Validar que la fecha no sea muy antigua
            if año < (fecha_actual.year - 2):
                raise ValidationError("No puede generar informes para años anteriores a {}".format(
                    fecha_actual.year - 2
                ))
        
        return cleaned_data
    

#agenda evaluaciones
class EvaluacionForm(forms.ModelForm):
    class Meta:
        model = Evaluacion
        fields = ['asignatura', 'fecha', 'observacion']
        widgets = {
            'fecha': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'observacion': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        profesor = kwargs.pop('profesor', None)
        super().__init__(*args, **kwargs)
        if profesor:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(profesor=profesor)

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        if fecha and fecha < timezone.now():
            raise ValidationError('La fecha de evaluación no puede ser en el pasado')
        return cleaned_data

#ANOTACIONES
class AnotacionForm(forms.ModelForm):
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        empty_label="Seleccione un curso",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_curso'})
    )
    alumno = forms.ModelChoiceField(
        queryset=Usuario.objects.none(),
        empty_label="Seleccione un alumno",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_alumno'})
    )
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    nivel = forms.ChoiceField(
        choices=Anotacion.NIVELES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Anotacion
        fields = ['curso', 'alumno', 'nivel', 'descripcion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'data' in kwargs:
            try:
                curso_id = kwargs['data'].get('curso')
                if curso_id:
                    self.fields['alumno'].queryset = Usuario.objects.filter(
                        rol='ALUMNO',
                        matriculas__curso_id=curso_id,
                        matriculas__estado='ACTIVO'
                    ).distinct()
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['alumno'].queryset = Usuario.objects.filter(
                rol='ALUMNO',
                matriculas__curso=self.instance.curso,
                matriculas__estado='ACTIVO'
            ).distinct()

    def clean(self):
        cleaned_data = super().clean()
        curso = cleaned_data.get('curso')
        alumno = cleaned_data.get('alumno')

        if curso and alumno:
            # Verificar si el alumno está matriculado en el curso
            matricula_existe = alumno.matriculas.filter(
                curso=curso,
                estado='ACTIVO'
            ).exists()

            if not matricula_existe:
                self.add_error('alumno', 'El alumno seleccionado no está matriculado en este curso')

        return cleaned_data
    
class EditarAsistenciaForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'max': timezone.now().strftime('%Y-%m-%dT%H:%M'),  # Restricción en el HTML
        }),
        label='Fecha y Hora',
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S.%f%z']
    )
    
    class Meta:
        model = RegistroAsistencia
        fields = ['estado', 'fecha_hora']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.fecha_hora:
            # Convertir la fecha de la base de datos al formato datetime-local
            local_datetime = self.instance.fecha_hora.astimezone()  # Convierte a la zona horaria local
            self.initial['fecha_hora'] = local_datetime.strftime('%Y-%m-%dT%H:%M')
            
            

class BitacoraSeleccionForm(forms.Form):
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.none(),
        label='Seleccione la asignatura',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha = forms.DateField(
        label='Fecha',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    observacion = forms.CharField(
        label='Observación',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la observación'
        })
    )

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(profesor=usuario)
