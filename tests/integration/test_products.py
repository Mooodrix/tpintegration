def test_create_product(client):
    # On simule l'envoi d'un formulaire JSON pour créer un produit
    response = client.post(
        "/products/",
        json={
            "name": "PC Gamer Intégration",
            "price": 1200.0,
            "stock": 5,
            "category": "Informatique"
        }
    )
    
    # On vérifie que le serveur répond "201 Created"
    assert response.status_code == 201
    
    # On vérifie que la réponse contient bien notre produit avec un ID généré
    data = response.json()
    assert data["name"] == "PC Gamer Intégration"
    assert data["price"] == 1200.0
    assert "id" in data

def test_get_products(client):
    # On simule un visiteur qui va sur la page d'accueil des produits
    response = client.get("/products/")
    
    # On vérifie que le serveur répond "200 OK"
    assert response.status_code == 200
    
    # On vérifie qu'il y a au moins notre PC Gamer dans la liste
    data = response.json()
    assert len(data) >= 1
    
    # On cherche notre produit dans la liste retournée
    noms_produits = [produit["name"] for produit in data]
    assert "PC Gamer Intégration" in noms_produits

def test_create_product_invalid_price(client):
    # On vérifie que notre vigile (Pydantic) bloque bien les mauvaises requêtes via l'API
    response = client.post(
        "/products/",
        json={"name": "Bug", "price": -50.0, "stock": 1}
    )
    
    # 422 = Unprocessable Entity (Erreur de validation Pydantic)
    assert response.status_code == 422