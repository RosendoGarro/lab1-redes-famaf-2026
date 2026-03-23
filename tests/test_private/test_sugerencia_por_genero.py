"""
Tests que debés implementar: sugerencia con filtro por género.
Completar los tests según el contrato de la API.
"""

import pytest
from src import store

@pytest.fixture
def setup_datos():
    """Fixture para preparar datos en las mismas referencias de memoria."""
    # vaciamos la lista y diccionario para no afectar otros tests
    store.USUARIOS.clear()
    store.CATALOGO_JUEGOS.clear()
    store.LISTAS_JUEGOS.clear()

    # llenamos "in_place" usando append y update
    store.USUARIOS.append({"id": 1, "nombre": "UsuarioTest", "username": "test_user"})
    store.CATALOGO_JUEGOS.update({
        "Q1": {"nombre": "Zelda", "genero": "Aventura", "lanzamiento": "2017", "plataforma": "Switch", "descripcion": "Juego de aventura"},
        "Q2": {"nombre": "Valorant", "genero": "Shooter", "lanzamiento": "2020", "plataforma": "PC", "descripcion": "Shooter táctico"},
        "Q3": {"nombre": "CS2", "genero": "Shooter", "lanzamiento": "2023", "plataforma": "PC", "descripcion": "Shooter clásico"}
    })
    
    store.LISTAS_JUEGOS.update({
        1: [
            {"juego_id": "Q1", "tengo": True, "quiero": False, "jugado": True, "me_gusta": True, "fecha_agregado": "2026-03-18"},
            {"juego_id": "Q2", "tengo": True, "quiero": False, "jugado": True, "me_gusta": True, "fecha_agregado": "2026-03-18"},
            {"juego_id": "Q3", "tengo": False, "quiero": True, "jugado": False, "me_gusta": False, "fecha_agregado": "2026-03-18"}
        ]
    })
    
    yield # mi test se ejecuta aqui 
    
    # limpiamos nuevamente para no afectar otros tests
    store.USUARIOS.clear()
    store.CATALOGO_JUEGOS.clear()
    store.LISTAS_JUEGOS.clear()


def test_sugerencia_con_genero_solo_devuelve_ese_genero(client, setup_datos):
    response = client.get("/usuarios/1/sugerencia?genero=Shooter")
    
    assert response.status_code == 200
    data = response.json
    
    assert data["id"] == "Q2"
    assert data["genero"] == "Shooter"
    assert data["nombre"] == "Valorant"


def test_sugerencia_genero_sin_coincidencias_404(client, setup_datos):
    response = client.get("/usuarios/1/sugerencia?genero=Deportes")
    
    assert response.status_code == 404
    assert "error" in response.json