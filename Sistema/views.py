from django.shortcuts import render, redirect, get_object_or_404
from .models import CalificacionTributaria, CambioRegistro, logAcceso, Notificacion
from .forms import CalificacionForm

# ==========================================================
# LOGIN Y DASHBOARDS
# ==========================================================
def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        password = request.POST.get("password")
        cargo = request.POST.get("cargo")

        # Redirección según el cargo seleccionado
        if cargo == "administrador":
            return redirect("admin_dashboard")
        elif cargo == "corredor":
            return redirect("corredor_dashboard")
        elif cargo == "auditor":
            return redirect("auditor_dashboard")
        else:
            return render(request, "login.html", {
                "error": "Debe seleccionar un cargo válido."
            })

    return render(request, "login.html")


# ==========================================================
# DASHBOARDS
# ==========================================================
def admin_dashboard(request):
    return render(request, "dashboard1.html")


def corredor_dashboard(request):
    return render(request, "dashboard2.html")


def auditor_dashboard(request):
    registro_cambio = CambioRegistro.objects.order_by('-fecha_cambio')[:5]
    registro_acceso = logAcceso.objects.order_by('-fecha_acceso')[:5]

    context = {
        'cambios': registro_cambio,
        'accesos': registro_acceso,
    }
    return render(request, "dashboard3.html", context)


# ==========================================================
# CRUD DE CALIFICACIONES TRIBUTARIAS
# ==========================================================
def listaCalificaciones(request):
    """Lista todas las calificaciones registradas y muestra formulario para crear."""
    calificaciones = CalificacionTributaria.objects.all().order_by('-fecha_creacion')
    form = CalificacionForm()
    return render(request, 'calificaciones/calificaciones.html', {
        'calificaciones': calificaciones,
        'form': form
    })


def crearCalificacion(request):
    """Crea una nueva calificación tributaria."""
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            # Temporalmente sin usuario_creador
            calificacion.save()

            # Registrar auditoría temporal
            CambioRegistro.objects.create(
                calificacion_modificada=calificacion,
                usuario=None,
                tipo_cambio='CREACION',
                detalle_registro=f"Creó la calificación de {calificacion.nombre_emisor}"
            )
            return redirect('listaCalificaciones')
    else:
        form = CalificacionForm()

    calificaciones = CalificacionTributaria.objects.all().order_by('-fecha_creacion')
    return render(request, 'calificaciones/calificaciones.html', {
        'form': form,
        'accion': 'Crear',
        'calificaciones': calificaciones
    })


def modCalificacion(request, id):
    """Modifica una calificación existente."""
    calificacion = get_object_or_404(CalificacionTributaria, id_calificacion=id)
    if request.method == 'POST':
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()

            # Registrar auditoría temporal
            CambioRegistro.objects.create(
                calificacion_modificada=calificacion,
                usuario=None,
                tipo_cambio='MODIFICACION',
                detalle_registro=f"Modificó la calificación de {calificacion.nombre_emisor}"
            )
            return redirect('listaCalificaciones')
    else:
        form = CalificacionForm(instance=calificacion)

    calificaciones = CalificacionTributaria.objects.all().order_by('-fecha_creacion')
    return render(request, 'calificaciones/calificaciones.html', {
        'form': form,
        'accion': 'Modificar',
        'calificaciones': calificaciones
    })


def eliminarCalificacion(request, id):
    """Elimina una calificación tributaria."""
    calificacion = get_object_or_404(CalificacionTributaria, id_calificacion=id)

    # Registrar auditoría temporal
    CambioRegistro.objects.create(
        calificacion_modificada=calificacion,
        usuario=None,
        tipo_cambio='ELIMINACION',
        detalle_registro=f"Eliminó la calificación de {calificacion.nombre_emisor}"
    )

    calificacion.delete()
    return redirect('listaCalificaciones')

# ==========================================================
# MOVILIDAD BÁSICA DEL AUDITOR
# ==========================================================

def consultaAuditor(request):
    cambios = CambioRegistro.objects.order_by('-fecha_cambio')
    return render(request, 'consultasAuditor.html',{"cambios":cambios})

def notificacionesAuditor(request):
    notificaciones = Notificacion.objects.order_by('-fecha')
    return render(request, 'notificacionesAuditor.html',{"notificaciones":notificaciones})

def registroAuditor(request):
    accesos = logAcceso.objects.order_by('-fecha_acceso')
    return render(request, 'accederRegistroAuditor.html',{"accesos":accesos})