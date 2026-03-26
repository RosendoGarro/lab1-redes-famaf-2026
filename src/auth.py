"""Versión INSEGURA de autenticación para el kickstarter.

Esta implementación es funcional pero tiene dos problemas graves:

- Guarda las contraseñas en texto plano (password_hash == password).
- No maneja expiración real de tokens (token_expira_en queda en NULL).

El objetivo de la Parte 6 del enunciado es justamente corregir estos
problemas en la solución final.
"""

from __future__ import annotations

import os
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from flask import jsonify

from werkzeug.security import generate_password_hash, check_password_hash

from . import auth_common
from .store import guardar_credenciales, actualizar_token


def _token_ttl_minutes() -> int:
    """TTL de tokens en minutos (default 60).

    En la versión insegura del kickstarter NO se usa para setear expiración;
    se deja como referencia para los estudiantes.
    """
    raw = os.environ.get("AUTH_TOKEN_TTL_MINUTES", "60")
    try:
        value = int(raw)
    except ValueError:
        return 60
    return max(1, value)


def registrar_usuario_auth():
    """Handler para POST /auth/registro (kickstarter, INSEGURO).

    - Crea el usuario correctamente.
    - Guarda la contraseña en texto plano en password_hash (esto está mal).
    """
    parsed, error = auth_common.parse_register_body()
    if error is not None:
        return error
    assert parsed is not None
    username = parsed["username"]
    nombre = parsed["nombre"]
    password = parsed["password"]

    dup_error = auth_common.ensure_username_unique(username)
    if dup_error is not None:
        return dup_error

    usuario = auth_common.crear_usuario_basico(nombre)

    # Hasheamos la contraseña antes de guardarla
    password_hash = generate_password_hash(password)
    guardar_credenciales(usuario["id"], username, password_hash)

    return jsonify(usuario), 201


def login():
    """Handler para POST /auth/login (kickstarter, INSEGURO).

    - Compara la contraseña en texto plano.
    - Genera un token sin fecha de expiración útil (token_expira_en = NULL).
    """
    parsed, error = auth_common.parse_login_body()
    if error is not None:
        return error
    assert parsed is not None
    username = parsed["username"]
    password = parsed["password"]

    cred, error = auth_common.get_credenciales_or_401(username)
    if error is not None:
        return error
    assert cred is not None

    # Comparamos usando el hash seguro
    if not check_password_hash(cred["password_hash"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = uuid4().hex
    ttl = _token_ttl_minutes()
    exp = datetime.now(timezone.utc) + timedelta(minutes=ttl)
    # Guardamos el ISO en UTC con Z para compatibilidad con tests
    exp_iso = exp.isoformat().replace("+00:00", "Z")
    actualizar_token(cred["usuario_id"], token, exp_iso)

    return jsonify({"token": token})


def obtener_usuario_actual() -> int | None:
    """Devuelve usuario_id asociado al token o None (kickstarter, sin expiración).

    - NO chequea expiración: cualquier token almacenado se considera válido.
    - Esto es inseguro; la solución final debe usar token_expira_en.
    """
    token = auth_common.extraer_token_de_header()
    if not token:
        return None
    data = auth_common.obtener_datos_token(token)
    if data is None:
        return None

    usuario_id = data.get("usuario_id")
    exp = data.get("token_expira_en")
    if not usuario_id or not exp:
        return None

    # Parse ISO that may end with Z
    try:
        if exp.endswith("Z"):
            exp_dt = datetime.fromisoformat(exp.replace("Z", "+00:00"))
        else:
            exp_dt = datetime.fromisoformat(exp)
    except Exception:
        return None

    if datetime.now(timezone.utc) > exp_dt:
        return None

    return int(usuario_id)

