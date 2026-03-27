import pytest
from app.models import Product, Cart, CartItem
from app.services.cart import get_or_create_cart, ajouter_au_panier, retirer_du_panier, calculer_total_ttc

# On utilise la vraie base de données en mémoire via db_session
def test_get_or_create_cart(db_session):
    # La première fois, ça doit créer le panier
    cart1 = get_or_create_cart(user_id=1, db=db_session)
    assert cart1.user_id == 1
    
    # La deuxième fois, ça doit retourner le MÊME panier
    cart2 = get_or_create_cart(user_id=1, db=db_session)
    assert cart1.id == cart2.id

def test_ajouter_au_panier(db_session):
    # On crée un produit en BDD
    product = Product(name="Souris", price=10.0)
    db_session.add(product)
    db_session.commit()
    
    # On ajoute au panier
    cart = ajouter_au_panier(product, 2, user_id=2, db=db_session)
    
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 2
    assert cart.items[0].product_id == product.id
    
    # On ajoute ENCORE le même produit (la quantité doit s'additionner)
    cart = ajouter_au_panier(product, 3, user_id=2, db=db_session)
    assert cart.items[0].quantity == 5

def test_retirer_du_panier(db_session):
    # Préparation
    product = Product(name="Clavier", price=50.0)
    db_session.add(product)
    db_session.commit()
    cart = ajouter_au_panier(product, 1, user_id=3, db=db_session)
    
    # Action : on retire
    cart = retirer_du_panier(cart, product.id, db=db_session)
    
    # Vérification
    assert len(cart.items) == 0
    
    # Erreur si on retire un produit qui n'est pas dans le panier
    with pytest.raises(ValueError, match="Produit introuvable dans le panier"):
        retirer_du_panier(cart, 999, db=db_session)

def test_calculer_total_ttc(db_session):
    product = Product(name="Ecran", price=100.0)
    db_session.add(product)
    db_session.commit()
    
    cart = ajouter_au_panier(product, 2, user_id=4, db=db_session) # 2 * 100 HT
    
    # 200 HT + 20% TVA = 240 TTC
    assert calculer_total_ttc(cart) == 240.0