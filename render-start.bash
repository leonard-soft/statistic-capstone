#!/bin/bash

# Movernos al subdirectorio donde está manage.py
cd DjangoProject

# Aplicar migraciones de Django por las apps internas
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Iniciar el servidor WSGI con Gunicorn
gunicorn DjangoProject.wsgi:application
