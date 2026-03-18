"""
Tests que debés implementar: casos borde de la lista de juegos.
Contrato: POST con juego_id (id del catálogo). Completar según openapi.yaml.
"""

import pytest


@pytest.fixture
def usuario_id(client):
    r = client.post("/usuarios", json={"nombre": "UsuarioBorde"})
    assert r.status_code == 201
    return r.get_json()["id"]


def test_agregar_juego_falta_campo_obligatorio_400(client, usuario_id):
    # TODO: POST sin un campo obligatorio (ej. juego_id) debe devolver 400
    pytest.skip("Implementar test")


def test_actualizar_juego_id_inexistente_404(client, usuario_id):
    # TODO: PUT /usuarios/<id>/juegos/Q99999 (no en lista) debe devolver 404
    pytest.skip("Implementar test")


def test_eliminar_juego_no_en_lista_404(client, usuario_id):
    # TODO: DELETE /usuarios/<id>/juegos/<juego_id> con juego no en la lista debe devolver 404
    pytest.skip("Implementar test")


def test_agregar_juego_id_inexistente_404(client, usuario_id):
    # TODO: POST con juego_id que no existe en catálogo ni Wikidata debe devolver 404
    pytest.skip("Implementar test")


def test_ordenar_por_fecha_lanzamiento(client, usuario_id):
    # TODO: GET juegos con ordenar=fecha_lanzamiento debe devolver ordenado
    pytest.skip("Implementar test")
