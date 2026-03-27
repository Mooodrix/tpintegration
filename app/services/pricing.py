MONTANT_MINIMUM_COUPON = 10.0
MONTANT_MINIMUM_GRATUIT = 50.0

def valider_coupon(coupon, panier_total: float) -> bool:
    """
    Valide qu'un coupon peut être appliqué sur un panier.
    Lève ValueError avec message explicite si une règle est violée.
    """
    if not coupon.actif:
        raise ValueError("Coupon inactif")
    if not (0 < coupon.reduction <= 100):
        raise ValueError("Valeur de réduction invalide")
    if panier_total < MONTANT_MINIMUM_COUPON:
        raise ValueError(f"Montant minimum de {MONTANT_MINIMUM_COUPON} non atteint")
    if coupon.reduction == 100 and panier_total < MONTANT_MINIMUM_GRATUIT:
        raise ValueError(f"Montant minimum de {MONTANT_MINIMUM_GRATUIT} non atteint pour un coupon gratuit")
    
    return True