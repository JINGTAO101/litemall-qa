from locust import HttpUser, task, between


class CartUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://127.0.0.1:8080"

    def on_start(self):
        r = self.client.post(
            "/wx/auth/login",
            json={"username": "user123", "password": "user123"},
        )
        token = r.json()["data"]["token"]
        self.client.headers["X-Litemall-Token"] = token

    @task
    def cart_index(self):
        self.client.get("/wx/cart/index")