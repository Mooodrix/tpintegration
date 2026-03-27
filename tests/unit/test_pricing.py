import pytest
from app.models import Product, Coupon
from app.services.pricing import calcul_prix_ttc, appliquer_coupon, calculer_total

# --- 1. Tests de calcul_prix_ttc ---
def test_calcul_prix_ttc_nominal():
    # Cas passant : 100€ HT -> 120€ TTC
    assert calcul_prix_ttc(100.0) == 120.0

def test_calcul_prix_ttc_zero():
    # Cas limite : 0€
    assert calcul_prix_ttc(0.0) == 0.0

def test_calcul_prix_ttc_erreur():
    # Cas d'erreur : prix négatif
    with pytest.raises(ValueError, match="Prix HT invalide"):
        calcul_prix_ttc(-10.0)

# --- 2. Tests de appliquer_coupon ---
def test_appliquer_coupon_valide():
    coupon = Coupon(code="PROMO20", reduction=20.0, actif=True)
    assert appliquer_coupon(100.0, coupon) == 80.0

def test_appliquer_coupon_inactif():
    coupon = Coupon(code="OLD", reduction=10.0, actif=False)
    with pytest.raises(ValueError, match="Coupon inactif"):
        appliquer_coupon(100.0, coupon)

def test_appliquer_coupon_reduction_invalide():
    coupon = Coupon(code="BUG", reduction=150.0, actif=True)
    with pytest.raises(ValueError, match="Reduction invalide"):
        appliquer_coupon(100.0, coupon)

# --- 3. Tests de calculer_total ---
def test_calculer_total_vide():
    assert calculer_total([]) == 0.0

def test_calculer_total_sans_coupon():
    p1 = Product(name="A", price=50.0) # HT
    p2 = Product(name="B", price=25.0) # HT
    panier = [(p1, 2), (p2, 1)] # Total HT = 100 + 25 = 125
    # TTC attendu = 125 * 1.20 = 150.0
    assert calculer_total(panier) == 150.0

def test_calculer_total_avec_coupon():
    p1 = Product(name="A", price=100.0)
    panier = [(p1, 1)] # Total HT = 100, TTC = 120
    coupon = Coupon(code="PROMO10", reduction=10.0, actif=True)
    # 120 - 10% = 108.0
    assert calculer_total(panier, coupon) == 108.0