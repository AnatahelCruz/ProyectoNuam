from django.shortcuts import render, redirect, get_object_or_404
from .models import CalificacionTributaria, CambioRegistro, logAcceso
from .forms import CalificacionForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import Role

# ==========================================================
# LOGIN Y DASHBOARDS
# ==========================================================
def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo").strip()
        password = request.POST.get("password").strip()
        cargo = request.POST.get("cargo")

        if not correo.endswith("@nuam.cl"):
            messages.error(request, "Su correo no es válido. Debe usar un correo @nuam.cl.")
            return redirect("login")

        try:
            user_obj = User.objects.get(username=correo)
        except User.DoesNotExist:
            messages.error(request, "Su correo no está registrado en el sistema.")
            return redirect("login")

        user = authenticate(request, username=correo, password=password)
        if user is None:
            messages.error(request, "Contraseña inválida. Inténtelo nuevamente.")
            return redirect("login")

        login(request, user)
        messages.success(request, f"Bienvenido, {user.username}.")

        if cargo == "administrador":
            return redirect("admin_dashboard")
        elif cargo == "corredor":
            return redirect("corredor_dashboard")
        elif cargo == "auditor":
            return redirect("auditor_dashboard")
        else:
            messages.warning(request, "Debe seleccionar un cargo válido.")
            return redirect("login")

    return render(request, "login.html")


# ==========================================================
# DASHBOARDS
# ==========================================================
@login_required
def admin_dashboard(request):
    return render(request, "dashboard1.html")

@login_required
def corredor_dashboard(request):
    return render(request, "dashboard2.html")

@login_required
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

def adminRequired(view_func):
    return user_passes_test(
        lambda u: u.is_superuser,
        login_url="login"
    )(view_func)

# 📌 LISTAR ROLES
@adminRequired
def listarRoles(request):
    roles = Role.objects.all()
    return render(request, "usuarios.html", {"roles": roles})


@adminRequired
def crearRol(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")

        if Role.objects.filter(nombre=nombre).exists():
            messages.error(request, "Ese rol ya existe.")
        else:
            Role.objects.create(nombre=nombre)
            messages.success(request, "Rol creado exitosamente.")

        return redirect("listarRoles")

    return redirect("listarRoles")


@adminRequired
def editarRol(request, id):
    rol = get_object_or_404(Role, id=id)

    if request.method == "POST":
        nuevoNombre = request.POST.get("nombre")
        rol.nombre = nuevoNombre
        rol.save()
        messages.success(request, "Rol actualizado correctamente.")
        return redirect("listarRoles")

    return render(request, "editarRol.html", {"rol": rol})


@adminRequired
def eliminarRol(request, id):
    rol = get_object_or_404(Role, id=id)
    rol.delete()
    messages.success(request, "Rol eliminado.")
    return redirect("listarRoles")