"""
URL configuration for nuamproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Sistema.views import (
    login_view, admin_dashboard, auditor_dashboard, corredor_dashboard,
    listaCalificaciones, crearCalificacion, modCalificacion, eliminarCalificacion, listarRoles,
    crearRol, editarRol, eliminarRol
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('corredor/', corredor_dashboard, name='corredor_dashboard'),
    path('auditor/', auditor_dashboard, name='auditor_dashboard'),
    path('calificaciones/', listaCalificaciones, name='listaCalificaciones'),
    path('calificaciones/crear/', crearCalificacion, name='crearCalificacion'),
    path('calificaciones/modificar/<int:id>/', modCalificacion, name='modCalificacion'),
    path('calificaciones/eliminar/<int:id>/', eliminarCalificacion, name='eliminarCalificacion'),
    path("roles/", listarRoles, name="listarRoles"),
    path("roles/crear/", crearRol, name="crearRol"),
    path("roles/editar/<int:id>/", editarRol, name="editarRol"),
    path("roles/eliminar/<int:id>/", eliminarRol, name="eliminarRol"),
]

