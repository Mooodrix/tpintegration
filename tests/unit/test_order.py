import pytest
from app.models import Product, Cart, CartItem, Order
from app.services.order import creer_commande, mettre_a_jour_statut
from app.services.cart import ajouter_au_panier

def test_creer_commande_succes(db_session, mocker):
    # On mock reserver_stock pour ne pas dépendre de la vraie fonction
    mock_reserver = mocker.patch("app.services.order.reserver_stock")

    # Préparation : un produit et un panier
    product = Product(name="Casque", price=100.0, stock=5)
    db_session.add(product)
    db_session.commit()
    
    cart = ajouter_au_panier(product, 2, user_id=1, db=db_session)

    # Action : créer la commande
    order = creer_commande(user_id=1, cart=cart, db=db_session)

    # Vérifications
    assert order.user_id == 1
    assert order.total_ht == 200.0  # 2 * 100
    assert order.status == "pending"
    assert len(order.items) == 1
    
    # Vérifier que le panier a été vidé (fonction appelée en interne)
    assert len(cart.items) == 0
    # Vérifier qu'on a bien appelé la réservation de stock
    mock_reserver.assert_called_once()

def test_mettre_a_jour_statut_succes(db_session):
    # Créer une commande de test
    order = Order(user_id=1, total_ht=100.0, total_ttc=120.0, status="pending")
    db_session.add(order)
    db_session.commit()

    # Mettre à jour
    updated_order = mettre_a_jour_statut(order.id, "shipped", db=db_session)

    assert updated_order.status == "shipped"

def test_mettre_a_jour_statut_erreur(db_session):
    # ID qui n'existe pas
    with pytest.raises(ValueError, match="Commande non trouvée"):
        mettre_a_jour_statut(999, "shipped", db=db_session)