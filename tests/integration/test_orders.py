def test_full_checkout_flow(client):
    # 1. L'admin crée un produit
    resp_prod = client.post(
        "/products/", 
        json={"name": "Clavier Mécanique", "price": 50.0, "stock": 10}
    )
    assert resp_prod.status_code == 201
    prod_id = resp_prod.json()["id"]

    # 2. Le client (user_id=1) l'ajoute à son panier (quantité: 2)
    resp_cart = client.post(
        "/cart/?user_id=1", 
        json={"product_id": prod_id, "quantity": 2}
    )
    assert resp_cart.status_code == 201
    assert resp_cart.json()["sous_total"] == 120.0  # (50 * 2) + 20% TVA

    # 3. Le client passe sa commande
    resp_order = client.post(
        "/orders/", 
        json={"user_id": 1}
    )
    assert resp_order.status_code == 201
    
    # 4. On vérifie que la facture est bonne
    order_data = resp_order.json()
    assert order_data["total_ht"] == 100.0
    assert order_data["status"] == "pending"
    assert len(order_data["items"]) == 1
    
    # 5. On vérifie que le panier a bien été vidé après l'achat
    resp_cart_after = client.get("/cart/1")
    assert len(resp_cart_after.json()["items"]) == 0