"""Sugerencia de un juego al azar desde la lista del usuario (opcional por género).

Qué es este módulo:
    Implementa el endpoint GET /usuarios/<id>/sugerir que devuelve un juego
    elegido al azar entre los que el usuario tiene (tengo=true), opcionalmente
    filtrado por género.

Para qué sirve:
    Dar una recomendación aleatoria al usuario basada en lo que ya tiene,
    útil para “¿qué juego juego hoy?” o para descubrir uno por género.

Qué hace:
    - _candidatos_que_tengo: obtiene los ítems con tengo=true del usuario.
    - _filtrar_candidatos_por_genero: filtra por género usando el catálogo.
    - _candidatos_sugerencia: combina ambos; None si el usuario no existe.
    - sugerir_juego: el endpoint; 404 si usuario no existe o no hay candidatos.
"""

import random
from flask import request, jsonify

from .store import USUARIOS, LISTAS_JUEGOS, CATALOGO_JUEGOS


def _candidatos_que_tengo(usuario_id: int) -> list[dict] | None:
    """Devuelve los ítems de la lista del usuario con tengo=true.

    Args:
        usuario_id: Id del usuario.

    Returns:
        Lista de ítems (dict con juego_id, flags, etc.); None si el usuario no existe.
    """
    if next((x for x in USUARIOS if x["id"] == usuario_id), None) is None:
        return None
    lista = LISTAS_JUEGOS.get(usuario_id, [])
    return [i for i in lista if i.get("tengo")]


def _filtrar_candidatos_por_genero(candidatos: list[dict], genero: str | None) -> list[dict]:
    """Filtra la lista de candidatos por género según el catálogo.

    Args:
        candidatos: Lista de ítems (con juego_id).
        genero: Género a filtrar; si es None, devuelve todos los candidatos.

    Returns:
        Lista de ítems cuyo juego tiene ese género en el catálogo.
    """
    if not genero:
        return candidatos
    
    # comparamos ignorando mayúsculas/minúsculas para ser más robustos y evitar que el usuario tenga que escribir exactamente el género como está en el catálogo
    genero_buscado = genero.lower()
    return [
        i for i in candidatos
        if CATALOGO_JUEGOS.get(i["juego_id"], {}).get("genero", "").lower() == genero_buscado
    ]


def _candidatos_sugerencia(usuario_id: int, genero: str | None) -> list[dict] | None:
    """Obtiene candidatos para sugerir: ítems con tengo=true, opcionalmente por género.

    Args:
        usuario_id: Id del usuario.
        genero: Género opcional para filtrar; None = todos.

    Returns:
        Lista de ítems candidatos; None si el usuario no existe.
    """
    candidatos = _candidatos_que_tengo(usuario_id)
    if candidatos is None:
        return None
    return _filtrar_candidatos_por_genero(candidatos, genero)


def sugerir_juego(usuario_id: int):
    """Sugiere un juego al azar entre los que el usuario tiene (tengo=true).

    Query param: genero (opcional) para filtrar por género.

    Args:
        usuario_id: Id del usuario.

    Returns:
        Response: JSON con id, nombre, descripcion, genero, lanzamiento, plataforma y 200;
        404 si el usuario no existe o no hay juegos que cumplan el criterio.
    """
    # obtenemos el parametro opcional de la URL
    genero = request.args.get("genero")
    
    # buscamos los candidatos usando las funciones helper
    candidatos = _candidatos_sugerencia(usuario_id, genero)
    
    # manejamos los casos de error "usuario no existe" y "no hay candidatos" 404
    if candidatos is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    if not candidatos:
        return jsonify({"error": "No hay juegos para sugerir con ese criterio"}), 404
        
    # elegimos un juego al azar de la lista filtrada
    item_elegido = random.choice(candidatos)
    
    # buscamos la info del juego en el catalogo para enriquecer la respuesta
    juego_cat = CATALOGO_JUEGOS.get(item_elegido["juego_id"], {})
    
    # armamos el JSON final respetando el esquema del contrato de la api
    resultado = {
        "id": item_elegido["juego_id"],
        "nombre": juego_cat.get("nombre", ""),
        "genero": juego_cat.get("genero", ""),
        "lanzamiento": juego_cat.get("lanzamiento", ""),
        "plataforma": juego_cat.get("plataforma", ""),
        "descripcion": juego_cat.get("descripcion", ""),
        "tengo": item_elegido.get("tengo", False),
        "quiero": item_elegido.get("quiero", False),
        "jugado": item_elegido.get("jugado", False),
        "me_gusta": item_elegido.get("me_gusta", False),
        "fecha_agregado": item_elegido.get("fecha_agregado", "")
    }
    
    return jsonify(resultado), 200