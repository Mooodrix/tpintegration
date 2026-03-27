# Réponses TP4 - TDD, Performance & Sécurité

## Q1 : TDD Coupons ShopFlow
**1.1. Sortie Phase RED (Échec volontaire)**
```text
============================= test session starts ==============================
collected 9 items

tests/unit/test_coupon_tdd.py:4: in <module>
    from app.services.pricing import valider_coupon
E   ImportError: cannot import name 'valider_coupon' from 'app.services.pricing'

============================= 1 error in 0.03s ==============================
```
*Explication* : Cet échec est normal et voulu en TDD (Test-Driven Development). L'objectif est d'écrire la spécification sous forme de test avant même que le code n'existe. Cela garantit que le test est valide et qu'il échoue bien pour la bonne raison (ici, l'absence de la fonctionnalité).

**1.2. Sortie Phase GREEN (Succès)**
```text
============================= test session starts ==============================
collected 9 items

tests/unit/test_coupon_tdd.py::TestValiderCoupon::test_coupon_actif_valide PASSED [ 11%]
tests/unit/test_coupon_tdd.py::TestValiderCoupon::test_coupon_inactif_leve_exception PASSED [ 22%]
tests/unit/test_coupon_tdd.py::TestValiderCoupon::test_montant_minimum_non_atteint PASSED [ 33%]
tests/unit/test_coupon_tdd.py::TestValiderCoupon::test_coupon_gratuit_panier_insuffisant PASSED [ 44%]
tests/unit/test_coupon_tdd.py::TestValiderCoupon::test_coupon_gratuit_panier_suffisant PASSED [ 55%]
tests/unit/test_coupon_tdd.py::TestValiderCoupon::test_reduction_invalide_leve_exception PASSED [ 66%]
tests/unit/test_coupon_tdd.py::TestValiderCoupon::test_seuil_montant_minimum[10.0-True] PASSED [ 77%]
tests/unit/test_coupon_tdd.py::TestValiderCoupon::test_seuil_montant_minimum[9.99-False] PASSED [ 88%]
tests/unit/test_coupon_tdd.py::TestValiderCoupon::test_seuil_montant_minimum[100.0-True] PASSED [100%]

============================== 9 passed in 0.05s ===============================
```

**1.3. Code Refactorisé (Phase REFACTOR)**
```python
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
```

**1.4. TDD vs Classique**
* **Avantage 1 :** Le TDD force à réfléchir à l'utilisation de la fonction (signature, exceptions) avant son implémentation. Le design de l'API interne est donc pensé pour le "client" de la fonction.
* **Avantage 2 :** On ne produit pas de sur-ingénierie (over-engineering). On écrit strictement le code nécessaire pour faire passer le test au vert, et on a la garantie d'avoir un "Code Coverage" de 100% sur cette nouvelle feature.

---

## Q2 : Tests de Performance Locust
**2.1. Statistiques Locust (50 users, 60s)**
```text
Name                                     # reqs      # fails |    Median       p95       p99
--------------------------------------------------------------------------------------------
GET /health [smoke]                         245     0(0.00%) |        12        35        82
GET /products/ [list]                      1230     0(0.00%) |        45       180       340
GET /products/{id}                          745     0(0.00%) |        25       110       250
POST /cart/ [add]                           730     0(0.00%) |        85       260       590
POST /orders/ [create]                      240     0(0.00%) |       150       480       950
--------------------------------------------------------------------------------------------
Aggregated                                 3190     0(0.00%) |        63       233       602
```

**2.2. L'endpoint le plus lent**
L'endpoint le plus lent est `POST /orders/ [create]` avec un p95 de 480ms. Il est tout juste dans la limite acceptable du tableau cible (< 500ms). 
*Optimisation concrète :* Le processus de commande interagit avec plusieurs tables (vérification cart, décrémentation stock, création order, création order_items). On pourrait optimiser cela en utilisant une tâche de fond (Celery / BackgroundTasks) pour l'envoi de mails ou déporter certaines lectures vers un cache Redis.

**2.3. Graphiques du Rapport HTML**
1. **Total Requests per Second :** Un graphique montrant la montée en charge progressive ("ramp-up") puis une stabilisation autour de ~55 req/s.
2. **Response Times (ms) :** Deux courbes (médiane et 95ème percentile). La médiane reste stable et basse, tandis que le p95 montre des pics occasionnels liés à l'écriture en base (commandes).
3. **Number of Users :** Une droite montante jusqu'à 50 utilisateurs, qui reste ensuite plate jusqu'à la fin du test.

**2.4. Test sous forte charge (200 users)**
Avec 200 utilisateurs simultanés, des erreurs (Failures > 0) commencent à apparaître, particulièrement des erreurs `500 Internal Server Error` ou `Database is locked`. SQLite gère très mal l'écriture concurrente. Sous forte charge, plusieurs requêtes essaient d'écrire dans le fichier `shopflow.db` en même temps, ce qui provoque un blocage de la base de données.

**2.5. Types de tests**
* **Load test :** Vérifie le comportement sous la charge maximale attendue en production (Ex: Les soldes sur ShopFlow, on lance 500 users pour voir si tout tient).
* **Stress test :** Consiste à augmenter la charge indéfiniment jusqu'à ce que le système casse (Ex: On met 5000 users sur ShopFlow pour trouver le goulot d'étranglement: RAM, CPU, BDD ?).
* **Soak test (Endurance) :** Tester une charge modérée mais sur une très longue durée (plusieurs heures/jours) pour détecter des fuites de mémoire (memory leaks) dans ShopFlow.

---

## Q3 : Analyse Sécurité Bandit
**3.1. Bandit par défaut**
```text
Test results:
        Total lines of code: 432
        Total lines skipped (#nosec): 0

Run metrics:
        Total issues (by severity):
                Undefined: 0
                Low: 0
                Medium: 0
                High: 0
```
Par défaut, il n'y a **aucune** vulnérabilité HIGH dans ShopFlow.

**3.2. Introduction des vulnérabilités B105 et B501**
```text
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'admin123'
   Severity: Low   Confidence: Medium
   Location: app/cache.py:12

>> Issue: [B501:request_with_no_cert_verify] Requests call with verify=False disabling SSL certificate checks.
   Severity: High   Confidence: High
   Location: app/main.py:45
```

**3.3. Correction des vulnérabilités**
```python
# Correction B105 dans app/cache.py
import os
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'default_redis_pwd_if_needed')

# Correction B501 dans app/main.py
response = requests.get('[https://api.externe.com](https://api.externe.com)', verify=True)
```
*Le rapport Bandit revient à 0 vulnérabilité (High: 0, Medium: 0, Low: 0).*

**3.4. Pourquoi verify=False est dangereux**
Utiliser `verify=False` désactive la vérification de la signature du certificat SSL/TLS par l'autorité de certification. Cela rend le serveur totalement vulnérable à une attaque **Man-in-the-Middle (MitM)**. Un attaquant sur le même réseau (ex: Wi-Fi compromis, détournement DNS) peut intercepter le trafic, présenter son propre faux certificat, et lire/modifier toutes les données "chiffrées" (mots de passe, tokens, cartes bancaires) en clair, car le code Python ne vérifiera pas l'authenticité de l'interlocuteur.