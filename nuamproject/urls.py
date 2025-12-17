
from django.contrib import admin
from django.urls import path
from Sistema.views import (
    login_view, admin_dashboard, auditor_dashboard, corredor_dashboard,
    listaCalificaciones, crearCalificacion, modCalificacion, eliminarCalificacion, eliminarUsuario, verMontosCorredor, ingresarMonto, editarMonto,
    eliminarMonto, verNotificacionesCorredor, registroAuditor, consultaAuditor,
    notificacionesAuditor, cargarArchivo, eliminarArchivo, register_user, logout_view,
    usuarios, asignarRol, eliminarRolUsuario, notificacionesAdmin, eliminarNotificacion, factores,
    guardarFactores, eliminarFactores
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'), 
    path("registro/", register_user, name="register_user"),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('corredor/', corredor_dashboard, name='corredor_dashboard'),
    path('auditor/', auditor_dashboard, name='auditor_dashboard'),
    path('usuarios/', usuarios, name='usuarios'),
    path('usuarios/asignar-rol/<int:user_id>/', asignarRol, name='asignarRol'),
    path('eliminar-usuario/<int:user_id>/', eliminarUsuario, name='eliminarUsuario'),
    path('usuarios/eliminar-rol/<int:user_id>/', eliminarRolUsuario, name='eliminarRolUsuario'),
    path('calificaciones/', listaCalificaciones, name='listaCalificaciones'),
    path('calificaciones/crear/', crearCalificacion, name='crearCalificacion'),
    path('calificaciones/modificar/<int:id>/', modCalificacion, name='modCalificacion'),
    path('calificaciones/eliminar/<int:id>/', eliminarCalificacion, name='eliminarCalificacion'),
    path('corredor/montos/', verMontosCorredor, name='verMontosCorredor'),
    path('corredor/montos/ingresar/', ingresarMonto, name='ingresarMonto'),
    path('corredor/montos/editar/', editarMonto, name='editarMonto'),
    path('corredor/montos/eliminar/', eliminarMonto, name='eliminarMonto'),
    path('corredor/notificaciones/', verNotificacionesCorredor, name='verNotificacionesCorredor'),
    path('corredor/factores/', factores, name='factores'),
    path('corredor/factores/guardar/', guardarFactores, name='guardarFactores'),
    path('corredor/factores/eliminar/', eliminarFactores, name='eliminarFactores'),
    path('auditor/registros/', registroAuditor, name='registros'),
    path('auditor/consultas/', consultaAuditor, name='consultas'),
    path('auditor/notificaciones/', notificacionesAuditor,name='notificaciones'),
    path('cargar-archivo/', cargarArchivo, name='cargarArchivo'),
    path('cargar-archivo/eliminar/<int:id>/', eliminarArchivo, name='eliminarArchivo'),
    path('notificaciones/', notificacionesAdmin, name='notificacionesAdmin'),
    path('notificaciones/eliminar/<int:notificacion_id>/', eliminarNotificacion, name='eliminarNotificacion'),

]

