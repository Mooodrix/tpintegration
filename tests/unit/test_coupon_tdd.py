import pytest
from app.services.pricing import valider_coupon
from app.models import Coupon

class TestValiderCoupon:
    def test_coupon_actif_valide(self):
        c = Coupon(code='PROMO20', reduction=20.0, actif=True)
        assert valider_coupon(c, panier_total=50.0) is True

    def test_coupon_inactif_leve_exception(self):
        c = Coupon(code='OLD', reduction=10.0, actif=False)
        with pytest.raises(ValueError, match='inactif'):
            valider_coupon(c, panier_total=50.0)

    def test_montant_minimum_non_atteint(self):
        c = Coupon(code='PROMO10', reduction=10.0, actif=True)
        with pytest.raises(ValueError, match='minimum'):
            valider_coupon(c, panier_total=5.0)

    def test_coupon_gratuit_panier_insuffisant(self):
        c = Coupon(code='FREE', reduction=100.0, actif=True)
        with pytest.raises(ValueError, match='50'):
            valider_coupon(c, panier_total=30.0)

    def test_coupon_gratuit_panier_suffisant(self):
        c = Coupon(code='FREE100', reduction=100.0, actif=True)
        assert valider_coupon(c, panier_total=50.0) is True

    def test_reduction_invalide_leve_exception(self):
        c = Coupon(code='BAD', reduction=0.0, actif=True)
        with pytest.raises(ValueError, match='réduction'):
            valider_coupon(c, panier_total=100.0)

    @pytest.mark.parametrize('total,attendu', [
        (10.0, True),
        (9.99, False),
        (100.0, True),
    ])
    def test_seuil_montant_minimum(self, total, attendu):
        c = Coupon(code='T1', reduction=10.0, actif=True)
        if attendu:
            assert valider_coupon(c, panier_total=total) is True
        else:
            with pytest.raises(ValueError):
                valider_coupon(c, panier_total=total)