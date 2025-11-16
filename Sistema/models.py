from django.db import models
from django.contrib.auth.models import User

class CalificacionTributaria(models.Model):
    id_calificacion = models.AutoField(primary_key=True)
    codigo_emisor = models.CharField(max_length=10, unique=True)
    nombre_emisor = models.CharField(max_length=100)
    tipo_instrumento = models.CharField(max_length=50)
    monto_bruto = models.DecimalField(max_digits=15, decimal_places=2)
    monto_neto = models.DecimalField(max_digits=15, decimal_places=2)
    retencion_impuesto = models.DecimalField(max_digits=15, decimal_places=2)
    fecha_emision = models.DateField()
    año_tributario = models.IntegerField()
    estado_calificacion = models.CharField(
        max_length=10,
        choices=[
            ('ACTIVA', 'Activa'),
            ('INACTIVA', 'Inactiva'),
            ('REVISION', 'Revisión'),
        ]
    )
    observaciones = models.TextField(blank=True, null=True)

    usuario_creador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='calificaciones_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    verificada_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calificaciones_verificadas'
    )

    def __str__(self):
        return f"{self.nombre_emisor} ({self.estado_calificacion})"


class CambioRegistro(models.Model):
    calificacion_modificada = models.ForeignKey(
        CalificacionTributaria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Calificación Tributaria modificada"
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    tipo_cambio = models.CharField(
        max_length=50,
        choices=[
            ('CREACION', 'Creación'),
            ('MODIFICACION', 'Modificación'),
            ('ELIMINACION', 'Eliminación'),
        ]
    )
    detalle_registro = models.TextField()

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo_cambio} ({self.fecha_cambio})"


class logAcceso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_acceso = models.DateTimeField(auto_now_add=True)
    tipo_accion = models.CharField(max_length=20)
    direccion_ip = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo_accion} ({self.fecha_acceso})"

class Notificacion(models.Model):

    TIPOS = [
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('info', 'Información'),
        ('success', 'Éxito'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.mensaje[:30]}"
