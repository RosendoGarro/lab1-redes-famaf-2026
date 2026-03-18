"""Lista de juegos por usuario: agregar, listar, actualizar y eliminar ítems; filtros y ordenación.

Qué es este módulo:
    Implementa los endpoints de la lista de juegos de cada usuario: GET/POST
    /usuarios/<id>/juegos y GET/PUT/DELETE /usuarios/<id>/juegos/<juego_id>.
    Cada ítem referencia un juego del catálogo (por juego_id, Q-id de Wikidata)
    y tiene flags: tengo, quiero, jugado, me_gusta, más fecha_agregado.

Para qué sirve:
    Permite que cada usuario tenga su propia lista de videojuegos con estado
    (lo tengo, lo quiero, lo jugué, me gusta). La lista se filtra y ordena
    según query params (genero, ordenar, orden).

Qué hace:
    - listar_juegos_usuario: devuelve la lista enriquecida con datos del catálogo; acepta genero, ordenar, orden.
    - agregar_juego_usuario: agrega un juego por juego_id (debe existir en catálogo o Wikidata); 409 si ya está.
    - actualizar_juego_usuario: actualiza los flags del ítem; 404 si el juego no está en la lista.
    - eliminar_juego_usuario: quita el juego de la lista; 404 si no está.

Qué se espera que hagas:
    En el kickstarter las funciones vienen con stubs. Implementá la lógica
    usando store.LISTAS_JUEGOS, store.CATALOGO_JUEGOS, wikidata.obtener_juego
    y filtros.filtrar_y_ordenar. Respetá los códigos 400, 404, 409 del contrato.
    Podés tomar como referencia el endpoint de ejemplo `crear_usuario` en
    `src/usuarios.py` para ver cómo se actualizan estructuras de `store`
    y se persisten los cambios antes de devolver la respuesta JSON.
"""

from datetime import datetime, timezone
from flask import request, jsonify

from .store import USUARIOS, LISTAS_JUEGOS, CATALOGO_JUEGOS, _persist_listas
from . import wikidata
from . import filtros


def _lista_usuario(usuario_id: int):
    """Devuelve la lista de ítems del usuario o None si el usuario no existe.

    Args:
        usuario_id: Id del usuario.

    Returns:
        Lista de ítems (dict con juego_id, tengo, quiero, jugado, me_gusta, fecha_agregado)
        o None si el usuario no existe.
    """
    
    usuario = next((u for u in USUARIOS if u["id"] == usuario_id), None)

    if not usuario:
        return None

    # Notar que esto puede devolver una lista vacía!
    return LISTAS_JUEGOS.get(usuario_id, [])



def _enriquecer_item(item: dict) -> dict | None:
    """Combina un ítem de la lista (juego_id + flags) con los datos del juego en el catálogo.

    Args:
        item: Dict con juego_id, tengo, quiero, jugado, me_gusta, fecha_agregado.

    Returns:
        Dict con todos los campos del juego (id, nombre, genero, etc.) más los flags;
        None si el juego_id no está en el catálogo.
    """
    juego = CATALOGO_JUEGOS.get(item["juego_id"])
    if not juego:
        return None
    return {
        "id": item["juego_id"],
        "nombre": juego.get("nombre", ""),
        "genero": juego.get("genero", ""),
        "lanzamiento": juego.get("lanzamiento", ""),
        "plataforma": juego.get("plataforma", ""),
        "descripcion": juego.get("descripcion", ""),
        "tengo": item.get("tengo", False),
        "quiero": item.get("quiero", False),
        "jugado": item.get("jugado", False),
        "me_gusta": item.get("me_gusta", False),
        "fecha_agregado": item.get("fecha_agregado", ""),
    }


def listar_juegos_usuario(usuario_id: int):
    """Lista los juegos del usuario con filtro y ordenación; enriquecidos con datos del catálogo.

    Query params: genero (opcional), ordenar (nombre, fecha_lanzamiento, fecha_agregado), orden (asc, desc).

    Args:
        usuario_id: Id del usuario.

    Returns:
        Response: JSON con lista de juegos (cada uno con id, nombre, flags, etc.) y 200;
        404 si el usuario no existe.
    """

    # Lista cruda de los juegos del usuario. Cada item en la lista es un 
    # diccionario mapeando juego_id -> status, donde status es 
    # {tengo, quiero, jugado, me gusta}
    lista_cruda = _lista_usuario(usuario_id)

    if lista_cruda is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    lista_enriquecida = []
    for item in lista_cruda:
        item_completo = _enriquecer_item(item)
        if item_completo is not None:  # enriquecer item puede tirar None
            lista_enriquecida.append(item_completo)

    genero = request.args.get("genero")
    ordenar = request.args.get("ordenar", "nombre") # nombre por defecto
    orden = request.args.get("orden", "asc") # ascendent por defecto

    # Llamamos a la función que la cátedra te dejó armada en src/filtros.py
    lista_final = filtros.filtrar_y_ordenar(
        items=lista_enriquecida,
        genero=genero,
        ordenar=ordenar,
        orden=orden,
        ordenes_validos=filtros.ORDEN_VALIDOS_LISTA
    )

    return jsonify(lista_final), 200


def _validar_body_agregar_juego():
    """Valida el body JSON de POST para agregar juego.

    Returns:
        (error_response, None) si hay error (400); (None, (juego_id, req)) si es válido.
    """
    if not request.json:
        return (jsonify({"error": "Datos inválidos"}), 400), None
    req = request.json
    for key in ("juego_id", "tengo", "quiero", "jugado", "me_gusta"):
        if key not in req:
            return (jsonify({"error": f"Datos inválidos: falta {key}"}), 400), None
    return None, (str(req["juego_id"]).strip(), req)


def _lista_y_existente(usuario_id: int, juego_id: str) -> tuple[list[dict] | None, dict | None]:
    """Obtiene la lista del usuario y el ítem existente (si el juego ya está en la lista).

    Args:
        usuario_id: Id del usuario.
        juego_id: Q-id del juego.

    Returns:
        (lista, item_existente). lista es None si el usuario no existe;
        item_existente es el dict del ítem si ya está en la lista, sino None.
    """
    if next((u for u in USUARIOS if u["id"] == usuario_id), None) is None:
        return None, None
    lista = LISTAS_JUEGOS.setdefault(usuario_id, [])
    existente = next((i for i in lista if i["juego_id"] == juego_id), None)
    return lista, existente


def agregar_juego_usuario(usuario_id: int):
    """Agrega un juego a la lista del usuario. El juego debe existir en catálogo o Wikidata.

    Request body (JSON): juego_id (str), tengo, quiero, jugado, me_gusta (bool).

    Args:
        usuario_id: Id del usuario.

    Returns:
        Response: JSON del ítem creado (enriquecido) y 201; 400 si falta campo, 404 si usuario
        o juego no existe, 409 si el juego ya está en la lista.
    """
    return jsonify({"error": "No implementado"}), 501


def actualizar_juego_usuario(usuario_id: int, juego_id: str):
    """Actualiza los flags (tengo, quiero, jugado, me_gusta) de un ítem de la lista.

    Args:
        usuario_id: Id del usuario.
        juego_id: Q-id del juego en la lista.

    Request body (JSON): campos opcionales tengo, quiero, jugado, me_gusta (bool).

    Returns:
        Response: JSON del ítem actualizado y 200; 404 si usuario o juego en lista no existe.
    """
    return jsonify({"error": "No implementado"}), 501


def eliminar_juego_usuario(usuario_id: int, juego_id: str):
    """Elimina un juego de la lista del usuario.

    Args:
        usuario_id: Id del usuario.
        juego_id: Q-id del juego a quitar de la lista.

    Returns:
        Response: JSON con mensaje de éxito y 200; 404 si usuario o juego en lista no existe.
    """
    return jsonify({"error": "No implementado"}), 501
