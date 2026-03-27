from sqlalchemy.orm import Session
from app.models import Cart, CartItem, Product
from app.services.pricing import calcul_prix_ttc

def get_or_create_cart(user_id: int, db: Session) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def ajouter_au_panier(product: Product, quantity: int, user_id: int, db: Session) -> Cart:
    cart = get_or_create_cart(user_id, db)
    item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product.id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        db.add(item)
    db.commit()
    db.refresh(cart)
    return cart

def retirer_du_panier(cart: Cart, product_id: int, db: Session) -> Cart:
    item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
    if not item:
        raise ValueError("Produit introuvable dans le panier")
    db.delete(item)
    db.commit()
    db.refresh(cart)
    return cart

def vider_panier(cart: Cart, db: Session):
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()

def calculer_total_ttc(cart: Cart) -> float:
    total_ht = sum(item.product.price * item.quantity for item in cart.items if item.product)
    return calcul_prix_ttc(total_ht)