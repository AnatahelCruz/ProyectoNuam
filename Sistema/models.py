from django.db import models
from django.contrib.auth.models import User

class Mercado(models.TextChoices):
    ACCIONES = "Acciones", "Acciones"
    FONDOS = "Fondos de Inversión", "Fondos de Inversión"
    BONOS = "Bonos", "Bonos"
    DERIVADOS = "Derivados", "Derivados"
    OTROS = "Otros", "Otros"


class Instrumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class CalificacionTributaria(models.Model):
    mercado = models.CharField(
        max_length=50,
        choices=Mercado.choices,
        default=Mercado.ACCIONES
    )
    instrumento = models.ForeignKey(Instrumento, on_delete=models.PROTECT, null=True)
    descripcion = models.CharField(max_length=250, default="")
    fecha_pago = models.DateField(null=True, blank=True)
    secuencia_evento = models.PositiveIntegerField(default=1)
    dividendo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    valor_historico = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    factor_actualizacion = models.DecimalField(max_digits=10, decimal_places=8, default=1)
    anio = models.PositiveIntegerField(verbose_name="Año", default=2025)
    isfut = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.instrumento.nombre if self.instrumento else 'Sin Instrumento'} - {self.fecha_pago}"

    def obtener_factores(self):
        return self.factores.order_by('numero')

    def factores_dict(self):
        return {f.numero: float(f.valor) for f in self.factores.all()}


class FactorTributario(models.Model):
    calificacion = models.ForeignKey(
        CalificacionTributaria,
        on_delete=models.CASCADE,
        related_name="factores"
    )
    numero = models.PositiveIntegerField()  # Ejemplo: 8...37
    valor = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    class Meta:
        unique_together = ('calificacion', 'numero')

    def __str__(self):
        return f"Factor {self.numero}: {self.valor}"


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


class Role(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Notificacion(models.Model):
    TIPOS = [
        ('success', 'Éxito'),
        ('danger', 'Error'),
        ('warning', 'Advertencia'),
        ('info', 'Información'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS)
    mensaje = models.CharField(max_length=255)
    actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="notificaciones_creadas")
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.mensaje[:30]}"


class MontoCorredor(models.Model):
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    liquido = models.DecimalField(max_digits=12, decimal_places=2)
    bruto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.valor} | Líquido: {self.liquido} | Bruto: {self.bruto}"


class ArchivoCargado(models.Model):
    TIPO_CHOICES = [
        ('FACTOR', 'Carga por Factor'),
        ('MONTO', 'Carga por Monto'),
    ]

    nombre_archivo = models.CharField(max_length=255)
    tipo_carga = models.CharField(max_length=10, choices=TIPO_CHOICES)
    fecha_carga = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f"{self.nombre_archivo} ({self.tipo_carga})"


class ArchivoDetalle(models.Model):
    archivo = models.ForeignKey(ArchivoCargado, on_delete=models.CASCADE, related_name='detalles')

    EJERCICIO = models.CharField(max_length=10, null=True, blank=True)
    MERCADO = models.CharField(max_length=10, null=True, blank=True)
    NEMO = models.CharField(max_length=100, null=True, blank=True)
    FEC_PAGO = models.CharField(max_length=20, null=True, blank=True)
    SEC_EVE = models.CharField(max_length=50, null=True, blank=True)
    DESCRIPCION = models.CharField(max_length=255, null=True, blank=True)

    F8 = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    F9 = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    F10 = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    F11 = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    F12 = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    F13 = models.DecimalField(max_digits=20, decimal_places=4, default=0)

    def __str__(self):
        return f"Detalle {self.id} - {self.archivo.nombre_archivo}"


class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} → {self.role.nombre}"
