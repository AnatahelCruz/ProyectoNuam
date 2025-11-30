import os
import pandas as pd
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from .models import (
    CalificacionTributaria,
    CambioRegistro,
    logAcceso,
    Notificacion,
    MontoCorredor,
    Role,
    ArchivoCargado,
    ArchivoDetalle,
    UserRole,
    Instrumento,
    FactorTributario
)

from .forms import CalificacionForm


# ==========================================================
# LOGIN / LOGOUT
# ==========================================================

def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        password = request.POST.get("password")

        user = authenticate(request, username=correo, password=password)

        if user is None:
            messages.error(request, "Correo o contraseña incorrectos.")
            return redirect("login")

        user_role = UserRole.objects.filter(user=user).first()
        if not user_role and not user.is_superuser:
            messages.error(request, "Tu cuenta no tiene permisos asignados para acceder.")
            return redirect("login")

        login(request, user)

        ip = request.META.get('REMOTE_ADDR')
        logAcceso.objects.create(
            usuario=user,
            tipo_accion="LOGIN",
            direccion_ip=ip
        )

        if user.is_superuser:
            return redirect("admin_dashboard")

        rol = user_role.role.nombre
        if rol == "Administrador":
            return redirect("admin_dashboard")
        elif rol == "Corredor":
            return redirect("corredor_dashboard")
        elif rol == "Auditor":
            return redirect("auditor_dashboard")
        else:
            messages.error(request, "Tu rol no tiene un panel asignado.")
            return redirect("login")

    return render(request, "login.html")


@login_required
def logout_view(request):
    if request.user.is_authenticated:
        ip = request.META.get('REMOTE_ADDR')
        logAcceso.objects.create(
            usuario=request.user,
            tipo_accion="LOGOUT",
            direccion_ip=ip
        )
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("login")

def adminRequired(view_func):
    return user_passes_test(lambda u: u.is_superuser, login_url="login")(view_func)
# ==========================================================
# REGISTRO DE USUARIOS
# ==========================================================

def register_user(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        correo = request.POST.get("correo")
        password = request.POST.get("password")

        if User.objects.filter(email=correo).exists():
            messages.error(request, "El correo ingresado ya está registrado.")
            return redirect("register_user")

        User.objects.create_user(
            username=correo,
            first_name=nombre,
            last_name=apellido,
            email=correo,
            password=password
        )

        messages.success(request, "Usuario registrado correctamente. Un administrador asignará tu rol.")
        return redirect("login")

    return render(request, "register.html")


@login_required
def usuarios(request):
    lista = User.objects.filter(is_superuser=False)
    data = []

    for u in lista:
        try:
            rol = UserRole.objects.get(user=u).role.nombre
        except UserRole.DoesNotExist:
            rol = "SIN ROL"

        data.append({
            "id": u.id,
            "nombre": u.first_name,
            "apellido": u.last_name,
            "correo": u.email,
            "rol": rol
        })

    return render(request, "usuarios.html", {"usuarios": data})


# ==========================================================
# ROLES
# ==========================================================

def adminRequired(view_func):
    return user_passes_test(lambda u: u.is_superuser, login_url="login")(view_func)


@adminRequired
def listarUsuarios(request):
    usuarios = User.objects.all()
    data = []

    for u in usuarios:
        try:
            rol = UserRole.objects.get(user=u).role.nombre
        except UserRole.DoesNotExist:
            rol = "SIN ROL"

        data.append({
            "id": u.id,
            "nombre": u.first_name,
            "apellido": u.last_name,
            "correo": u.email,
            "rol": rol
        })

    return render(request, 'usuarios.html', {'usuarios': data})


@adminRequired
def asignarRol(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        rol_nombre = request.POST.get('rol')

        if rol_nombre not in ['Administrador', 'Corredor', 'Auditor']:
            mensaje = "Rol no válido."
            messages.error(request, mensaje)
            Notificacion.objects.create(
                tipo='danger',
                mensaje=f"Intento de asignación de rol inválido a {usuario.username}",
                detalle=f"Se intentó asignar el rol '{rol_nombre}'",
                actor=request.user
            )
            return redirect('usuarios')

        rol, created = Role.objects.get_or_create(nombre=rol_nombre)
        UserRole.objects.update_or_create(user=usuario, defaults={'role': rol})

        messages.success(request, f"Rol '{rol.nombre}' asignado a {usuario.username}.")
        Notificacion.objects.create(
            tipo='success',
            mensaje=f"Rol '{rol.nombre}' asignado a {usuario.username}",
            detalle=f"El administrador asignó el rol {rol.nombre} a {usuario.username}."
        )

    return redirect('usuarios')


@adminRequired
def eliminarRolUsuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    try:
        user_role = UserRole.objects.get(user=usuario)
        user_role.delete()
        messages.success(request, f"Rol eliminado de {usuario.username}.")
        Notificacion.objects.create(
            tipo='info',
            mensaje=f"Rol eliminado de {usuario.username}",
            detalle=f"El administrador eliminó el rol de {usuario.username}."
        )
    except UserRole.DoesNotExist:
        mensaje = "El usuario no tiene rol asignado."
        messages.warning(request, mensaje)
        Notificacion.objects.create(
            tipo='warning',
            mensaje=f"No se pudo eliminar rol de {usuario.username}",
            detalle="El usuario no tenía rol asignado."
        )

    return redirect('usuarios')



@login_required
@adminRequired
def eliminarUsuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    try:
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        Notificacion.objects.create(
            tipo='warning',
            mensaje=f"Usuario {usuario.username} eliminado",
            detalle="El administrador eliminó este usuario del sistema."
        )
    except:
        mensaje = "Error al eliminar usuario."
        messages.error(request, mensaje)
        Notificacion.objects.create(
            tipo='danger',
            mensaje=f"Error al eliminar usuario {usuario.username}",
            detalle="No se pudo eliminar el usuario por un error desconocido."
        )

    return redirect("usuarios")

# ==========================================================
# DASHBOARDS
# ==========================================================

@login_required
@adminRequired
def admin_dashboard(request):

    ultimas_notificaciones = Notificacion.objects.order_by('-fecha')[:2]


    ultimos_archivos = ArchivoCargado.objects.order_by('-fecha_carga')[:2]


    usuarios = User.objects.filter(is_superuser=False).order_by('-date_joined')[:2]
    ultimos_usuarios = []
    for u in usuarios:
        try:
            rol = UserRole.objects.get(user=u).role.nombre
        except UserRole.DoesNotExist:
            rol = "SIN ROL"
        ultimos_usuarios.append({
            "nombre": u.first_name,
            "apellido": u.last_name,
            "correo": u.email,
            "rol": rol
        })

    context = {
        "ultimas_notificaciones": ultimas_notificaciones,
        "ultimos_archivos": ultimos_archivos,
        "ultimos_usuarios": ultimos_usuarios
    }

    return render(request, "dashboard1.html", context)


@login_required
def corredor_dashboard(request):
    if request.user.is_superuser:
        puede_acceder = True
    else:
        user_role = UserRole.objects.filter(user=request.user).first()
        puede_acceder = user_role and user_role.role.nombre == "Corredor"

    if not puede_acceder:
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect("login")

    ultimas_calificaciones = CalificacionTributaria.objects.order_by('-fecha_pago')[:3]
    calificaciones_data = [
        {
            "instrumento": c.instrumento.nombre if c.instrumento else "Sin Instrumento",
            "mercado": c.mercado,
            "fecha_pago": c.fecha_pago
        }
        for c in ultimas_calificaciones
    ]

    ultimas_notificaciones = CambioRegistro.objects.order_by('-fecha_cambio')[:3]

    context = {
        "ultimas_calificaciones": calificaciones_data,
        "ultimas_notificaciones": ultimas_notificaciones
    }

    return render(request, "dashboard2.html", context)



@login_required
def auditor_dashboard(request):
    if not request.user.is_superuser:
        user_role = UserRole.objects.filter(user=request.user).first()
        if not user_role or user_role.role.nombre != "Auditor":
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("login")
        
    ultimasNotificaciones = Notificacion.objects.order_by('-fecha')[:2]
    ultimosCambios = CambioRegistro.objects.order_by('-fecha_cambio')[:2]
    ultimosAccesos = logAcceso.objects.order_by('-fecha_acceso')[:2]
    context = {
        "notificaciones": ultimasNotificaciones,
        "cambios": ultimosCambios,
        "accesos": ultimosAccesos,
    }
    return render(request, "dashboard3.html", context)


# ==========================================================
# CALIFICACIONES TRIBUTARIAS
# ==========================================================

@login_required
def listaCalificaciones(request):
    calificaciones = CalificacionTributaria.objects.all().order_by('-fecha_pago')
    form = CalificacionForm()

    return render(request, "corredor/calificaciones.html", {
        "calificaciones": calificaciones,
        "form": form,
        "accion": None
    })


@login_required
def crearCalificacion(request):
    if request.method == "POST":
        form = CalificacionForm(request.POST)

        instrumento_nombre = request.POST.get("instrumento_nombre")
        if instrumento_nombre:
            instrumento, _ = Instrumento.objects.get_or_create(nombre=instrumento_nombre)
            form.instance.instrumento = instrumento

        if form.is_valid():
            try:
                calificacion = form.save()
                messages.success(request, "Calificación creada correctamente.")

                CambioRegistro.objects.create(
                    calificacion_modificada=calificacion,
                    usuario=request.user,
                    tipo_cambio="CREACION",
                    detalle_registro=f"Se creo una nueva calificación para {calificacion.instrumento}"
                )

                return redirect("listaCalificaciones")

            except Exception as e:
                messages.error(request, f"Error al guardar la calificación: {e}")

        calificaciones = CalificacionTributaria.objects.all().order_by('-fecha_pago')
        return render(request, "corredor/calificaciones.html", {
            "calificaciones": calificaciones,
            "form": form,
            "accion": None
        })

    return redirect("listaCalificaciones")

@login_required
def modCalificacion(request, id):
    calificacion = get_object_or_404(CalificacionTributaria, id=id)

    if request.method == "POST":
        form = CalificacionForm(request.POST, instance=calificacion)

        instrumento_nombre = request.POST.get("instrumento_nombre")
        if instrumento_nombre:
            instrumento, _ = Instrumento.objects.get_or_create(nombre=instrumento_nombre)
            form.instance.instrumento = instrumento

        if form.is_valid():
            try:
                calificacion = form.save()
                messages.success(request, "Calificación modificada correctamente.")

                CambioRegistro.objects.create(
                    calificacion_modificada=calificacion,
                    usuario=request.user,
                    tipo_cambio="MODIFICACION",
                    detalle_registro=f"Se modificó la calificación {calificacion.id}"
                )

                return redirect("listaCalificaciones")

            except Exception as e:
                messages.error(request, f"Error al modificar: {e}")

        return render(request, "corredor/calificaciones.html", {
            "calificaciones": CalificacionTributaria.objects.all().order_by('-fecha_pago'),
            "form": form,
            "accion": "Modificar"
        })

    form = CalificacionForm(instance=calificacion)
    return render(request, "corredor/calificaciones.html", {
        "calificaciones": CalificacionTributaria.objects.all().order_by('-fecha_pago'),
        "form": form,
        "accion": "Modificar"
    })

@login_required
def eliminarCalificacion(request, id):
    calificacion = get_object_or_404(CalificacionTributaria, id=id)
    nombre_instr = calificacion.instrumento.nombre

    CambioRegistro.objects.create(
        calificacion_modificada=calificacion,
        usuario=request.user,
        tipo_cambio="ELIMINACION",
        detalle_registro=f"Se eliminó la calificación del instrumento {nombre_instr}"
    )

    calificacion.delete()

    messages.warning(request, f"La calificación del instrumento '{nombre_instr}' fue eliminada correctamente.")

    return redirect("listaCalificaciones")


# ==========================================================
# MONTOS (Corredor)
# ==========================================================

def verMontosCorredor(request):
    montos = MontoCorredor.objects.all().order_by('-fecha_creacion')
    return render(request, "corredor/montos.html", {"montos": montos})


def ingresarMonto(request):
    if request.method == "POST":
        try:
            valor = float(request.POST.get("valor", 0))
            bruto = float(request.POST.get("bruto", 0))
        except ValueError:
            messages.error(request, "Valores inválidos.")
            return redirect("verMontosCorredor")

        liquido = valor - bruto

        if MontoCorredor.objects.filter(valor=valor, liquido=liquido, bruto=bruto).exists():
            messages.warning(request, "Este monto ya fue registrado.")
        else:
            MontoCorredor.objects.create(valor=valor, liquido=liquido, bruto=bruto)
            messages.success(request, "Monto registrado exitosamente.")

    return redirect("verMontosCorredor")


def editarMonto(request):
    if request.method == "POST":
        monto_id = request.POST.get("monto_id")
        try:
            monto = MontoCorredor.objects.get(id=monto_id)
            monto.liquido = request.POST.get("liquido")
            monto.bruto = request.POST.get("bruto")
            monto.save()
            messages.success(request, "Monto actualizado.")
        except:
            messages.error(request, "Error al actualizar.")
    return redirect("verMontosCorredor")


def eliminarMonto(request):
    if request.method == "POST":
        monto_id = request.POST.get("monto_id")
        try:
            monto = MontoCorredor.objects.get(id=monto_id)
            monto.delete()
            messages.success(request, "Monto eliminado.")
        except:
            messages.error(request, "Error al eliminar.")
    return redirect("verMontosCorredor")


def verNotificacionesCorredor(request):
    tipo = request.GET.get("tipo")
    notificaciones = CambioRegistro.objects.order_by('-fecha_cambio')
    if tipo:
        notificaciones = notificaciones.filter(tipo_cambio=tipo)
    return render(request, "corredor/notificaciones.html", {"notificaciones": notificaciones})


# ==========================================================
# AUDITOR
# ==========================================================

def consultaAuditor(request):
    cambios = CambioRegistro.objects.order_by('-fecha_cambio')
    return render(request, "consultasAuditor.html", {"cambios": cambios})


def notificacionesAuditor(request):
    notificaciones = Notificacion.objects.order_by('-fecha')
    return render(request, "notificacionesAuditor.html", {"notificaciones": notificaciones})


def registroAuditor(request):
    accesos = logAcceso.objects.order_by('-fecha_acceso')
    return render(request, "accederRegistroAuditor.html", {"accesos": accesos})


# ==========================================================
# CARGA DE ARCHIVOS (ADMIN)
# ==========================================================

@login_required
@adminRequired
def cargarArchivo(request):
    if request.method == "POST":
        archivo = request.FILES.get("archivo")
        tipo = request.POST.get("tipo_carga")

        if not archivo:
            mensaje = "Debe seleccionar un archivo."
            messages.error(request, mensaje)
            Notificacion.objects.create(
                tipo='danger',
                mensaje="Error al cargar archivo",
                detalle=mensaje
            )
            return redirect("cargarArchivo")

        if tipo not in ("FACTOR", "MONTO"):
            mensaje = "Debe seleccionar el tipo de carga."
            messages.error(request, mensaje)
            Notificacion.objects.create(
                tipo='danger',
                mensaje="Error al cargar archivo",
                detalle=mensaje
            )
            return redirect("cargarArchivo")

        nombre = archivo.name
        valid_ext = (".xlsx", ".xls", ".csv")

        if not nombre.lower().endswith(valid_ext):
            mensaje = "Formato inválido. Solo se permiten .xlsx, .xls, .csv"
            messages.error(request, mensaje)
            Notificacion.objects.create(
                tipo='danger',
                mensaje=f"Error al subir archivo {nombre}",
                detalle=mensaje
            )
            return redirect("cargarArchivo")

        nuevo = ArchivoCargado.objects.create(nombre_archivo=nombre, tipo_carga=tipo)
        nuevo.archivo.save(nombre, archivo, save=True)

        try:
            file_path = nuevo.archivo.path
            if nombre.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(file_path, dtype=str)
            else:
                df = pd.read_csv(file_path, dtype=str)

            df.columns = [c.strip().upper() for c in df.columns]

            required_min = [
                "EJERCICIO", "MERCADO", "NEMO", "FEC_PAGO",
                "SEC_EVE", "DESCRIPCION",
                "F8", "F9", "F10", "F11", "F12", "F13"
            ]

            missing = [c for c in required_min if c not in df.columns]
            if missing:
                nuevo.delete()
                mensaje = f"Faltan columnas requeridas: {', '.join(missing)}."
                messages.error(request, mensaje)
                Notificacion.objects.create(
                    tipo='danger',
                    mensaje=f"Error al subir archivo {nombre}",
                    detalle=mensaje
                )
                return redirect("cargarArchivo")

            detalles = []
            for _, row in df.iterrows():
                def parse_decimal(val):
                    try:
                        if val is None:
                            return 0
                        s = str(val).replace(",", "").strip()
                        if s == "" or s.upper() == "NAN":
                            return 0
                        return float(s)
                    except:
                        return 0

                detalles.append(
                    ArchivoDetalle(
                        archivo=nuevo,
                        EJERCICIO=row.get("EJERCICIO"),
                        MERCADO=row.get("MERCADO"),
                        NEMO=row.get("NEMO"),
                        FEC_PAGO=row.get("FEC_PAGO"),
                        SEC_EVE=row.get("SEC_EVE"),
                        DESCRIPCION=row.get("DESCRIPCION"),
                        F8=parse_decimal(row.get("F8")),
                        F9=parse_decimal(row.get("F9")),
                        F10=parse_decimal(row.get("F10")),
                        F11=parse_decimal(row.get("F11")),
                        F12=parse_decimal(row.get("F12")),
                        F13=parse_decimal(row.get("F13")),
                    )
                )

            ArchivoDetalle.objects.bulk_create(detalles)
            mensaje = f"Archivo '{nombre}' cargado correctamente."
            messages.success(request, mensaje)
            Notificacion.objects.create(
                tipo='success',
                mensaje=f"Archivo {nombre} cargado correctamente",
                detalle="El archivo se procesó y guardó sin errores."
            )
            return redirect("cargarArchivo")

        except Exception as e:
            nuevo.delete()
            mensaje = f"Error procesando archivo: {e}"
            messages.error(request, mensaje)
            Notificacion.objects.create(
                tipo='danger',
                mensaje=f"Error al procesar archivo {nombre}",
                detalle=str(e)
            )
            return redirect("cargarArchivo")

    archivos = ArchivoCargado.objects.order_by('-fecha_carga')
    return render(request, "cargarArchivo.html", {"archivos": archivos})

@login_required
@adminRequired
def eliminarArchivo(request, id):
    if request.method != "POST":
        mensaje = "Método no permitido."
        messages.error(request, mensaje)
        Notificacion.objects.create(
            tipo='danger',
            mensaje="Intento inválido de eliminar archivo",
            detalle=mensaje
        )
        return redirect("cargarArchivo")

    archivo = get_object_or_404(ArchivoCargado, id=id)

    try:
        ruta = archivo.archivo.path
        archivo.delete()
        if os.path.exists(ruta):
            os.remove(ruta)
        messages.success(request, "Archivo eliminado correctamente.")
        Notificacion.objects.create(
            tipo='warning',
            mensaje=f"Archivo {archivo.nombre_archivo} eliminado",
            detalle="El administrador eliminó este archivo del sistema."
        )
    except Exception as e:
        mensaje = f"Error al eliminar archivo: {e}"
        messages.error(request, mensaje)
        Notificacion.objects.create(
            tipo='danger',
            mensaje=f"Error al eliminar archivo {archivo.nombre_archivo}",
            detalle=str(e)
        )
    return redirect("cargarArchivo")

@login_required
@adminRequired
def notificacionesAdmin(request):
    notificaciones = Notificacion.objects.order_by('-fecha')
    return render(request, "notificacionesAdmin.html", {"notificaciones": notificaciones})

@login_required
@adminRequired
def eliminarNotificacion(request, notificacion_id):
    noti = get_object_or_404(Notificacion, id=notificacion_id)
    noti.delete()
    messages.success(request, "Notificación eliminada correctamente.")
    return redirect("notificacionesAdmin")


# ==========================================================
# FACTORES(COR)
# ==========================================================

@login_required
def factores(request):
    calificaciones = CalificacionTributaria.objects.all()
    calificacion_seleccionada = None
    factores_existentes = []

    nombres_factores = {
        'F8':'No constitutiva de Renta No Acogido a Impto.',
        'F9':'Impto. 1ra Categ. Afecto GI. Comp. Con Devolución',
        'F10':'Impuesto Tasa Adicional Exento Art.21',
        'F11':'Incremento Impuesto 1ra Categoría',
        'F12':'Impto. 1ra Categ. Exento GI. Comp. Con Devolución',
        'F13':'Impto. 1ra Categ. Afecto GI. Comp. Sin Devolución',
        'F14':'Impto. 1ra Categ. Exento GI. Comp. Sin Devolución',
        'F15':'Impto. Créditos pro Impuestos Externos',
        'F16':'No Constitutiva de Renta Acogido a Impto.',
        'F17':'No Constitutiva de Renta de Capital Art.17',
        'F18':'Rentas Exentas de Impto. GC Y/O Impto Adicional',
        'F19':'Ingreso no Constitutivos de Renta',
        'F20':'Sin Derecho a Devolución',
        'F21':'Con Derecho a Devolución',
        'F22':'Sin Derecho a Devolución',
        'F23':'Con Derecho a Devolución',
        'F24':'Sin Derecho a Devolución',
        'F25':'Con Derecho a Devolución',
        'F26':'Sin Derecho a Devolución',
        'F27':'Con Derecho a Devolución',
        'F28':'Crédito por IPE',
        'F29':'Sin Derecho a Devolución',
        'F30':'Con Derecho a Devolución',
        'F31':'Sin Derecho a Devolución',
        'F32':'Con Derecho a Devolución',
        'F33':'Crédito por IPE',
        'F34':'Créd. Por Impto. Tasa Adicional, Ex Art. 21 LIR',
        'F35':'Tasa Efectiva del Créd. Del FUT (TEF)',
        'F36':'Tasa Efectiva Del Créd. Del FUNT (TEX)',
        'F37':'Devolución de Capital Art. 17 num 7 LIR',
        'F38':'DESCRIPCIÓN'
    }

    cal_id = request.GET.get('calificacion_id')
    if cal_id:
        calificacion_seleccionada = get_object_or_404(CalificacionTributaria, id=cal_id)
        factores_existentes = calificacion_seleccionada.factores.all()

    return render(request, "corredor/factores.html", {
        "calificaciones": calificaciones,
        "calificacion_seleccionada": calificacion_seleccionada,
        "factores_existentes": factores_existentes,
        "nombres_factores": nombres_factores
    })


@login_required
def guardarFactores(request):
    if request.method == "POST":
        calificacion_id = request.POST.get("calificacion_id")
        ingreso_montos = request.POST.get("ingreso_montos") == "on"

        calificacion = get_object_or_404(CalificacionTributaria, id=calificacion_id)

        # Crear/Actualizar factores 8-37
        for i in range(8, 38):
            valor = request.POST.get(f'factor_{i}', 0) or 0
            FactorTributario.objects.update_or_create(
                calificacion=calificacion,
                numero=i,
                defaults={"valor": valor}
            )

        # Actualizar ISFUT
        calificacion.isfut = request.POST.get("isfut") == "on"
        calificacion.save()

        messages.success(request, "Factores guardados correctamente.")
        return redirect(f"/corredor/factores/?calificacion_id={calificacion_id}")

    return HttpResponseForbidden()


@login_required
def eliminarFactores(request):
    if request.method == "POST":
        calificacion_id = request.POST.get("calificacion_id")
        factores_a_eliminar = request.POST.getlist("eliminar_factores")

        calificacion = get_object_or_404(CalificacionTributaria, id=calificacion_id)

        FactorTributario.objects.filter(
            calificacion=calificacion,
            numero__in=factores_a_eliminar
        ).delete()

        messages.warning(request, "Factores eliminados correctamente.")
        return redirect(f"/corredor/factores/?calificacion_id={calificacion_id}")

    return HttpResponseForbidden()


