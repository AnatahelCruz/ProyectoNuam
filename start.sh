#!/bin/bash

# Migraciones automáticas
python manage.py migrate --noinput

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Inicia Gunicorn para servir Django
gunicorn nuamproject.wsgi