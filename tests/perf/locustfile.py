from locust import HttpUser, task, between
import random

PRODUCT_IDS = list(range(1, 21))

class ShopFlowUser(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self):
        self.user_id = random.randint(10000, 99999)

    @task(5)
    def browse_products(self):
        self.client.get('/products/', name='/products/ [list]')

    @task(3)
    def get_product_detail(self):
        pid = random.choice(PRODUCT_IDS)
        self.client.get(f'/products/{pid}', name='/products/{id}')

    @task(2)
    def add_to_cart(self):
        self.client.post(
            f'/cart/?user_id={self.user_id}', 
            json={"product_id": random.choice(PRODUCT_IDS), "quantity": 1},
            name='/cart/ [add]'
        )

    @task(1)
    def place_order(self):
        self.client.post(
            f'/cart/?user_id={self.user_id}', 
            json={"product_id": random.choice(PRODUCT_IDS), "quantity": 1},
            name='/cart/ [add]'
        )
        with self.client.post('/orders/', json={"user_id": self.user_id}, name='/orders/ [create]', catch_response=True) as response:
            if response.status_code in [201, 400]: # On accepte 400 si le panier est vide suite à une concurrence
                response.success()

    @task(1)
    def health_check(self):
        self.client.get('/health', name='/health [smoke]')