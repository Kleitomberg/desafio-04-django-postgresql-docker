import os
import socket

from django.conf import settings
from django.db import connection
from django.shortcuts import render


def home(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]
        db_ok = True
    except Exception as exc:
        db_version = str(exc)
        db_ok = False

    db = settings.DATABASES["default"]
    context = {
        "container_id": socket.gethostname(),
        "debug": settings.DEBUG,
        "db_ok": db_ok,
        "db_version": db_version,
        "db_host": db["HOST"],
        "db_port": db["PORT"],
        "db_name": db["NAME"],
        "db_user": db["USER"],
        "python_pid": os.getpid(),
    }
    return render(request, "app/home.html", context)
