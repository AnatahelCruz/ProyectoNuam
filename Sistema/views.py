from django.shortcuts import render, redirect
from .models import CalificacionTributaria
from .forms import CalificacionForm

# -------------------------------
# Login y Dashboard
# -------------------------------
def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        password = request.POST.get("password")
        cargo = request.POST.get("cargo")

        if cargo == "administrador":
            return redirect("admin_dashboard")  
        else:
            return render(request, "login.html", {
                "error": "Solo el administrador tiene acceso por ahora."
            })

    return render(request, "login.html")


def admin_dashboard(request):
    return render(request, "dashboard1.html")


# -------------------------------
# CRUD Calificaciones Tributarias
# -------------------------------

def listaCalificaciones(request):
    calificaciones = CalificacionTributaria.objects.all()
    return render(request, 'calificaciones.html', {'calificaciones': calificaciones})

def crearCalificacion(request):
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listaCalificaciones')
    else:
        form = CalificacionForm()
    return render(request, 'calificaciones.html', {'form': form})

def modCalificacion(request, id):
    calificacion = CalificacionTributaria.objects.filter(id=id).first()
    if not calificacion:
        return ("Calificación no encontrada")
    if request.method == 'POST':
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            return redirect('listaCalificaciones')
    else:
        form = CalificacionForm(instance=calificacion)
    return render(request, 'calificaciones.html', {'form': form})

def eliminarCalificacion(request, id):
    calificacion = CalificacionTributaria.objects.filter(id=id).first()
    if calificacion:
        calificacion.delete()
    return redirect('listaCalificaciones')

def ingresarMonto(request):
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listaCalificaciones')
    else:
        form = CalificacionForm()
    return render(request, 'calificaciones.html', {'form': form})
