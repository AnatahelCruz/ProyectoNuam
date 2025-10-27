from django.db import models

class CalificacionTributaria(models.Model):
    contribuyente = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.contribuyente} - {self.monto}"
