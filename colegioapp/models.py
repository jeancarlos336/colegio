from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError




# Modelo para los días de la semana
class DiaSemana(models.Model):
    nombre = models.CharField(
        max_length=10, 
        unique=True, 
        choices=[
            ('LUNES', 'Lunes'),
            ('MARTES', 'Martes'),
            ('MIERCOLES', 'Miércoles'),
            ('JUEVES', 'Jueves'),
            ('VIERNES', 'Viernes'),
            ('SABADO', 'Sábado'),
        ]
    )
    
    def __str__(self):
        return self.nombre

# Modelo de Sede
   
class Sede(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"

# Modelo personalizado de Usuario

class Usuario(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('PROFESOR', 'Profesor'),
        ('ALUMNO', 'Alumno'),
        ('APODERADO', 'Apoderado'),
        ('SECRETARIA', 'Secretaria'),
        ('DIRECTOR', 'Director'),
    )
    
    rol = models.CharField(max_length=20, choices=ROLES)
    rut = models.CharField(max_length=12, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    def obtener_sedes(self):
        """
        Devuelve las sedes en las que el usuario tiene asignaciones.
        """
        try:
            return Sede.objects.filter(profesores_asignados__usuario=self)
        except Exception:
            return Sede.objects.none()
    
    def obtener_dias_trabajados(self, sede=None):
        """
        Devuelve los días trabajados por el usuario en una sede específica o en todas.
        """
        try:
            queryset = self.asignaciones_sede.all()
            if sede:
                queryset = queryset.filter(sede=sede)
            return [asignacion.dias_trabajados.all() for asignacion in queryset]
        except Exception:
            return []    
    
    def __str__(self):
        """
        Retorna el nombre completo del usuario si está disponible,
        de lo contrario, retorna el username.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


# Modelo de Asignación de Profesor a Sede
class AsignacionProfesorSede(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='asignaciones_sede')
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='profesores_asignados')
    dias_trabajados = models.ManyToManyField(DiaSemana, related_name='asignaciones')
    
    class Meta:
        unique_together = ('usuario', 'sede')
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.sede.nombre}"

# Modelo de Curso
class Curso(models.Model):
    NIVELES = (
        ('PREESCOLAR', 'Preescolar'),
        ('BASICA', 'Básica'),
        ('MEDIA', 'Media'),
    )
    
    nombre = models.CharField(max_length=50)
    nivel = models.CharField(max_length=20, choices=NIVELES)
    año = models.IntegerField()
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='cursos')
    profesor_jefe = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='cursos_dirigidos')
    
    def __str__(self):
        return f"{self.nombre} - {self.sede.nombre} - {self.año}"

# Modelo de Asignatura actualizado

class Asignatura(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField(blank=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='asignaturas')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='asignaturas', null=True, blank=True)
    profesor = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'rol': 'PROFESOR'}, related_name='asignaturas')
    
    def __str__(self):
        return f"{self.nombre} - {self.sede.nombre} {f'- {self.curso.nombre}' if self.curso else ''}"


class RegistroAsistencia(models.Model):
    matricula = models.ForeignKey('Matricula', on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)  # Cambiado a auto_now_add
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=(
        ('PRESENTE', 'Presente'),
        ('AUSENTE', 'Ausente'),
        ('JUSTIFICADO', 'Justificado')
    ))
    
    class Meta:
        unique_together = ('matricula', 'fecha_hora', 'asignatura')


# Modelo de Calificación
        
class Calificacion(models.Model):
    TIPO_CHOICES = [
        ('NOTA 1', 'Nota 1'),
        ('NOTA 2', 'Nota 2'),
        ('NOTA 3', 'Nota 3'),
        ('NOTA 4', 'Nota 4'),
        ('NOTA 5', 'Nota 5')
    ]
    matricula = models.ForeignKey('Matricula', on_delete=models.CASCADE, related_name='calificaciones')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nota = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(1.0), MaxValueValidator(7.0)],
        null=True,  # Permite valores nulos en la base de datos
        blank=True  # Hace que sea opcional en formularios
    )
    semestre = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    especificacion = models.CharField(max_length=255, null=True, blank=True)  # Por consistencia
     
    class Meta:
        unique_together = ('matricula', 'asignatura', 'semestre', 'tipo')



# Modelo de Apoderado
class Apoderado(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    alumnos = models.ManyToManyField(
        Usuario, 
        related_name='apoderados', 
        limit_choices_to={'rol': 'ALUMNO'}
    )
    parentesco = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Apoderado de {', '.join(alumno.get_full_name() for alumno in self.alumnos.all())}"    


# Modelo de Matrícula

class Matricula(models.Model):
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='matriculas')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='matriculados')
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='matriculas')
    año = models.IntegerField()
    estado = models.CharField(max_length=20, choices=(
        ('ACTIVO', 'Activo'),
        ('RETIRADO', 'Retirado'),
        ('GRADUADO', 'Graduado')
    ))
    fecha_creacion = models.DateTimeField(default=timezone.now)
    usuario_creacion = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='matriculas_creadas'
    )

    class Meta:
        unique_together = ('alumno', 'curso', 'año', 'sede')



# Modelo de Horario
class Horario(models.Model):
    asignacion_profesor_sede = models.ForeignKey(AsignacionProfesorSede, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    dia = models.ForeignKey(DiaSemana, on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    def __str__(self):
        return f"{self.asignacion_profesor_sede.usuario.get_full_name()} - {self.asignatura.nombre} - {self.dia.nombre}"


class PagoMensualidad(models.Model):
    MESES = [
        ('ENERO', 'Enero'), ('FEBRERO', 'Febrero'), ('MARZO', 'Marzo'),
        ('ABRIL', 'Abril'), ('MAYO', 'Mayo'), ('JUNIO', 'Junio'),
        ('JULIO', 'Julio'), ('AGOSTO', 'Agosto'), ('SEPTIEMBRE', 'Septiembre'),
        ('OCTUBRE', 'Octubre'), ('NOVIEMBRE', 'Noviembre'), ('DICIEMBRE', 'Diciembre'),
    ]
    
    matricula = models.ForeignKey('Matricula', on_delete=models.CASCADE, related_name='pagos_mensualidad')
    mes = models.CharField(max_length=20, choices=MESES)
    año = models.IntegerField()
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    fecha_pago = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=(
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
    ), default='PENDIENTE')
    
    class Meta:
        unique_together = ('matricula', 'mes', 'año')
        constraints = [
            models.CheckConstraint(
                check=models.Q(año__lte=timezone.now().year),
                name='año_no_futuro'
            )
        ]
    
    def __str__(self):
        return f"{self.matricula.alumno.get_full_name()} - {self.mes} {self.año} - {self.estado}"


class Evaluacion(models.Model):
    asignatura = models.ForeignKey(
        'Asignatura', 
        on_delete=models.CASCADE,
        related_name='evaluaciones'
    )
    fecha = models.DateTimeField()
    observacion = models.TextField(blank=True)
    profesor = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='evaluaciones'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def clean(self):
        if self.fecha and self.fecha < timezone.now():
            raise ValidationError('La fecha de evaluación no puede ser en el pasado')
        if hasattr(self, 'profesor') and hasattr(self, 'asignatura') and self.asignatura and self.profesor != self.asignatura.profesor:
            raise ValidationError('Solo el profesor asignado puede crear evaluaciones para esta asignatura')

    def __str__(self):
        return f"Evaluación de {self.asignatura.nombre} - {self.fecha}"
    