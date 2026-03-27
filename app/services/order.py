from sqlalchemy.orm import Session
from app.models import Order, OrderItem, Cart, Coupon
from app.services.cart import vider_panier
from app.services.stock import reserver_stock
from app.services.pricing import calculer_total

def creer_commande(user_id: int, cart: Cart, db: Session, coupon: Coupon = None) -> Order:
    produits = [(item.product, item.quantity) for item in cart.items]
    for p, q in produits:
        reserver_stock(p, q, db)
        
    total_ttc = calculer_total(produits, coupon)
    total_ht = sum(p.price * q for p, q in produits)
    
    order = Order(
        user_id=user_id,
        total_ht=total_ht,
        total_ttc=total_ttc,
        coupon_code=coupon.code if coupon else None,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    for p, q in produits:
        order_item = OrderItem(order_id=order.id, product_id=p.id, quantity=q, unit_price=p.price)
        db.add(order_item)
        
    vider_panier(cart, db)
    db.commit()
    db.refresh(order)
    return order

def mettre_a_jour_statut(order_id: int, status: str, db: Session) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError("Commande non trouvée")
        
    # --- LA CORRECTION EST ICI : Logique métier bloquant pending -> shipped ---
    if order.status == "pending" and status == "shipped":
        raise ValueError("Transition invalide")
        
    order.status = status
    db.commit()
    db.refresh(order)
    return order