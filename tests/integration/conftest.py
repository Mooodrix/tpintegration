import pytest
from fastapi.testclient import TestClient
from faker import Faker
from app.main import app
from app.database import get_db
from sqlalchemy.orm import sessionmaker

fake = Faker('fr_FR')

@pytest.fixture(scope='module')
def client(db_session):
    """TestClient FastAPI avec BDD SQLite isolée par module de test."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def api_product(client):
    """Crée un produit via POST /products/ et le retourne."""
    response = client.post('/products/', json={
        'name': 'Clavier Mécanique',
        'price': 89.99,
        'stock': 25,
        'category': 'peripheriques'
    })
    assert response.status_code == 201
    data = response.json()
    yield data
    # Cleanup : on supprime le produit après le test
    client.delete(f'/products/{data["id"]}')

@pytest.fixture
def api_coupon(client):
    """Crée un coupon TEST10 (-10%) via POST /coupons/."""
    response = client.post('/coupons/', json={
        'code': 'TEST10', 'reduction': 10.0, 'actif': True
    })
    assert response.status_code == 201
    yield response.json()

@pytest.fixture
def fake_product_data():
    """Génère un payload produit réaliste et aléatoire avec Faker."""
    return {
        'name': fake.catch_phrase()[:50],
        'price': round(fake.pyfloat(min_value=1, max_value=2000, right_digits=2), 2),
        'stock': fake.random_int(min=0, max=500),
        'category': fake.random_element(['informatique', 'peripheriques', 'audio', 'gaming'])
    }

@pytest.fixture
def multiple_products(client):
    """Crée 5 produits avec faker pour tester la liste et les filtres."""
    products = []
    for i in range(5):
        r = client.post('/products/', json={
            'name': fake.word().capitalize() + f' {i}',
            'price': round(10.0 + i * 20, 2),
            'stock': 10
        })
        products.append(r.json())
    yield products
    # Cleanup : désactiver les 5 produits
    for p in products:
        client.delete(f'/products/{p["id"]}')