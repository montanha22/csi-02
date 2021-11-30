from flask.app import Flask
from flask.testing import FlaskClient
import pytest
import importlib
# csi_project = importlib.import_module("csi_project")
from csi_project import create_app
import json
import io
from PIL import Image

@pytest.fixture
def app() -> Flask:
    app = create_app()
    return app

@pytest.fixture
def client(app: Flask):

    with app.test_client() as client:
    # Establish an application context
        with app.app_context():
            yield client

def test_dumb(app):
    app

def test_app_exists(app):
    assert app is not None

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_api_acidentes(client):
    response = client.get('/api/v1/acidentes', data = {'start_month': '2020-01', 'end_month': '2020-02'})
    data = json.loads(response.data)

    assert response.status_code == 200
    assert len(data) == 1903

def test_api_vendas(client):
    response = client.get('/api/v1/vendas', data = {'start_month': '2020-01', 'end_month': '2020-02'})
    data = json.loads(response.data)
    sales_sum = sum([int(d['vendas']) for d in data])

    assert response.status_code == 200
    assert sales_sum == 319665

def test_api_grafico_vendas_mes(client: FlaskClient):
    response = client.get('/api/v1/grafico-vendas-por-mes', data = {'start_month': '2020-01', 'end_month': '2020-02'})
    data = response.data
    assert response.status_code == 200
    image = Image.open(io.BytesIO(data))
    assert response.mimetype == 'image/jpeg'



def test_api_grafico_acidentes_fatais_mes(client: FlaskClient):
    response = client.get('/api/v1/grafico-acidentes-fatais-por-mes', data = {'start_month': '2020-01', 'end_month': '2020-02'})
    data = response.data
    assert response.status_code == 200
    image = Image.open(io.BytesIO(data))
    assert response.mimetype == 'image/jpeg'


def test_api_grafico_acidentes_mes(client: FlaskClient):
    response = client.get('/api/v1/grafico-acidentes-por-mes', data = {'start_month': '2020-01', 'end_month': '2020-02'})
    data = response.data
    assert response.status_code == 200
    image = Image.open(io.BytesIO(data))
    assert response.mimetype == 'image/jpeg'

def test_api_grafico_acidentes_versus_vendas(client: FlaskClient):
    response = client.get('/api/v1/grafico-acidentes-versus-vendas', data = {'start_month': '2020-01', 'end_month': '2020-02'})
    data = response.data
    assert response.status_code == 200
    image = Image.open(io.BytesIO(data))
    assert response.mimetype == 'image/jpeg'


