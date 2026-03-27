# Réponses TP2 - Tests d'Intégration

## Q1 : Configuration TestClient
**1.1 Configuration initiale**
Le fichier `conftest.py` a bien été configuré avec la fixture `client` remplaçant la base de données par une BDD SQLite isolée en mémoire (`sqlite:///:memory:`).

**1.2 Scope de la fixture client**
Dans la fixture `client`, on utilise `scope='module'` plutôt que `function` car cela permet de créer la base de données et le client FastAPI **une seule fois par fichier de test**. Cela rend les tests beaucoup plus rapides. L'inconvénient est que la BDD est partagée entre les tests du même fichier, l'isolation n'est donc pas totale (contrairement à `function` qui recrée une BDD vierge à chaque test).

**1.3 Assertion dans la fixture api_product**
On fait le `assert response.status_code == 201` à l'intérieur de la fixture `api_product` pour s'assurer que l'étape de préparation (Arrange) a bien fonctionné. Si la création du produit échoue en amont, le test s'arrête immédiatement au lieu de planter plus loin avec une erreur incompréhensible.

---

## Q2 : Tests /products
**2.1 Tests CRUD Produits**
Voici la sortie de l'exécution du fichier `test_products_api.py` :
```text
============================= test session starts ==============================
collected 17 items

tests/integration/test_products_api.py::TestListProducts::test_liste_vide_au_demarrage PASSED [  5%]
tests/integration/test_products_api.py::TestListProducts::test_produit_cree_apparait_dans_liste PASSED [ 11%]
tests/integration/test_products_api.py::TestListProducts::test_filtre_par_categorie PASSED [ 17%]
tests/integration/test_products_api.py::TestListProducts::test_pagination_limit PASSED [ 23%]
tests/integration/test_products_api.py::TestListProducts::test_pagination_skip PASSED [ 29%]
tests/integration/test_products_api.py::TestGetProduct::test_get_produit_existant PASSED [ 35%]
tests/integration/test_products_api.py::TestGetProduct::test_get_produit_inexistant_retourne_404 PASSED [ 41%]
tests/integration/test_products_api.py::TestGetProduct::test_schema_complet PASSED [ 47%]
tests/integration/test_products_api.py::TestCreateProduct::test_creation_valide PASSED [ 52%]
tests/integration/test_products_api.py::TestCreateProduct::test_creation_prix_negatif_422 PASSED [ 58%]
tests/integration/test_products_api.py::TestCreateProduct::test_creation_nom_vide_422 PASSED [ 64%]
tests/integration/test_products_api.py::TestCreateProduct::test_creation_stock_negatif_422 PASSED [ 70%]
tests/integration/test_products_api.py::TestCreateProduct::test_active_true_par_defaut PASSED [ 76%]
tests/integration/test_products_api.py::TestUpdateDeleteProduct::test_mise_a_jour_prix PASSED [ 82%]
tests/integration/test_products_api.py::TestUpdateDeleteProduct::test_mise_a_jour_stock PASSED [ 88%]
tests/integration/test_products_api.py::TestUpdateDeleteProduct::test_suppression_soft_delete PASSED [ 94%]
tests/integration/test_products_api.py::TestUpdateDeleteProduct::test_filtre_prix_min_max PASSED [100%]

============================== 17 passed in 0.78s ==============================
```

**2.2 Filtre min/max**
Le test `test_filtre_prix_min_max` a bien été ajouté et exécuté avec succès. Il valide que les paramètres de requête `min_price` et `max_price` filtrent correctement les résultats de l'API.

---

## Q3 : Tests Panier & Commandes
**3.1 Tests du Panier (TestCart)**
Les tests d'ajout au panier, de calcul de sous-total et de vérification des stocks ont été implémentés. Une erreur 400 est bien levée si on tente d'ajouter un produit en rupture de stock.

**3.2 Tests des Commandes (TestOrders)**
Voici la sortie globale des tests de panier et de commandes :
```text
============================= test session starts ==============================
collected 15 items

tests/integration/test_cart_api.py::TestCart::test_ajout_produit_au_panier PASSED [  6%]
tests/integration/test_cart_api.py::TestCart::test_sous_total_calcule PASSED [ 13%]
tests/integration/test_cart_api.py::TestCart::test_ajout_stock_insuffisant_400 PASSED [ 20%]
tests/integration/test_cart_api.py::TestCart::test_ajout_meme_produit_incremente_quantite PASSED [ 26%]
tests/integration/test_cart_api.py::TestCart::test_vider_panier PASSED [ 33%]
tests/integration/test_orders_api.py::TestOrders::test_creation_commande_valide PASSED [ 40%]
tests/integration/test_orders_api.py::TestOrders::test_total_ttc_correct PASSED [ 46%]
tests/integration/test_orders_api.py::TestOrders::test_commande_decremente_stock PASSED [ 53%]
tests/integration/test_orders_api.py::TestOrders::test_commande_vide_le_panier PASSED [ 60%]
tests/integration/test_orders_api.py::TestOrders::test_panier_vide_retourne_400 PASSED [ 66%]
tests/integration/test_orders_api.py::TestOrders::test_commande_avec_coupon PASSED [ 73%]
tests/integration/test_orders_api.py::TestOrders::test_statut_pending_vers_confirmed PASSED [ 80%]
tests/integration/test_orders_api.py::TestOrders::test_transition_invalide_400 PASSED [ 86%]
tests/integration/test_orders_api.py::TestOrders::test_coupon_inexistant_retourne_404 PASSED [ 93%]
tests/integration/test_orders_api.py::TestOrders::test_get_commande_par_id PASSED [100%]

============================== 15 passed in 1.14s ==============================
```

**3.3 et 3.4 Coupon inexistant et Récupération par ID**
Comme visible dans les logs ci-dessus, les tests `test_coupon_inexistant_retourne_404` et `test_get_commande_par_id` passent avec succès. Des contrôles stricts ont été ajoutés dans le service métier (`app/services/order.py`) pour bloquer les transitions de statut illogiques (ex: `pending` vers `shipped`).

---

## Q4 : Données de Test & Faker
**4.1 Fixture Faker**
La librairie `faker` a été intégrée dans `conftest.py` pour générer des données de test réalistes et aléatoires. 

**4.3 Pourquoi utiliser Faker('fr_FR') ?**
Utiliser `Faker('fr_FR')` au lieu de `Faker()` permet de générer des données localisées (noms à consonance française, etc.). Dans le contexte de ShopFlow, si l'API possède des règles de validation strictes liées à la localisation (ex: format d'un numéro de téléphone), utiliser des données françaises permet d'éviter les faux positifs lors des tests, garantissant que les tests reflètent l'usage réel des utilisateurs ciblés.

---

## Q5 : JUnit XML & Synthèse
**5.1 Smoke Tests (test_health.py)**
Voici la sortie de nos smoke tests :
```text
tests/integration/test_health.py::TestHealth::test_health_ok PASSED [ 25%]
tests/integration/test_health.py::TestHealth::test_root_accessible PASSED [ 50%]
tests/integration/test_health.py::TestHealth::test_docs_swagger_accessible PASSED [ 75%]
tests/integration/test_health.py::TestHealth::test_openapi_json_accessible PASSED [100%]
============================== 4 passed in 0.65s ===============================
```

**5.2 Coverage Total**
Le coverage ciblé sur la couche applicative (`app/services`) a été atteint avec succès :
```text
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
app\services\cart.py         35      7    80%   27-33
app\services\order.py        32      1    97%   38
app\services\pricing.py      21      4    81%   8, 13, 15, 20
app\services\stock.py        27      9    67%   10, 14-20, 24
-------------------------------------------------------
TOTAL                       115     21    81%

Required test coverage of 80% reached. Total coverage: 81.42%
```
L'objectif de qualité de 80% imposé par le fichier `.coveragerc` est bien respecté et bloquera la CI en cas de régression.