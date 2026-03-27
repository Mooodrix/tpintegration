import pytest
from app.models import Product
from app.services.stock import verifier_stock, reserver_stock, liberer_stock

# On utilise une fixture pytest simple pour avoir un produit de test
@pytest.fixture
def test_product():
    return Product(id=1, name="Laptop", stock=10)

# --- 1. Tests de verifier_stock ---
def test_verifier_stock_suffisant(test_product):
    assert verifier_stock(test_product, 5) is True

def test_verifier_stock_insuffisant(test_product):
    assert verifier_stock(test_product, 15) is False

def test_verifier_stock_invalide(test_product):
    with pytest.raises(ValueError, match="Quantité invalide"):
        verifier_stock(test_product, -2)

# --- 2. Tests de reserver_stock (avec Mock de Redis) ---
def test_reserver_stock_succes(test_product, mocker):
    # On MOCK (simule) le redis_client
    mock_redis = mocker.patch("app.services.stock.redis_client")
    # On MOCK la session de base de données (on ne veut pas tester la BDD ici)
    mock_session = mocker.MagicMock()

    # On appelle la fonction
    result = reserver_stock(test_product, 3, mock_session)

    # Vérifications
    assert result.stock == 7  # Le stock a bien diminué
    mock_session.commit.assert_called_once()  # On a bien sauvegardé en base
    mock_redis.delete.assert_called_once_with("product:1:stock") # Le cache a bien été invalidé

def test_reserver_stock_echec(test_product, mocker):
    mock_session = mocker.MagicMock()
    with pytest.raises(ValueError, match="Stock insuffisant"):
        reserver_stock(test_product, 15, mock_session)

# --- 3. Tests de liberer_stock (avec Mock de Redis) ---
def test_liberer_stock_succes(test_product, mocker):
    mock_redis = mocker.patch("app.services.stock.redis_client")
    mock_session = mocker.MagicMock()

    result = liberer_stock(test_product, 2, mock_session)

    assert result.stock == 12 # Le stock a bien augmenté
    mock_session.commit.assert_called_once()
    mock_redis.set.assert_called_once_with("product:1:stock", 12) # Le cache a bien été mis à jour