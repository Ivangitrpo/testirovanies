 
from locust import HttpUser, task, between
import json

class OpenBMCUser(HttpUser):

    wait_time = between(1, 3)
    
  
    host = "https://127.0.0.1:2443"
    
    def on_start(self):
  

        self.client.verify = False
        

        auth_response = self.client.post(
            "/redfish/v1/SessionService/Sessions",
            json={"UserName": "root", "Password": "0penBmc"},
            headers={"Content-Type": "application/json"}
        )
        
     
        self.headers = {
            "X-Auth-Token": auth_response.headers["X-Auth-Token"],
            "Content-Type": "application/json"
        }

    @task(3) 
    def get_system_info(self):
        """Запрос информации о системе"""
        self.client.get(
            "/redfish/v1/Systems/system",
            headers=self.headers,
            name="(OpenBMC) Get System Info"  
        )

    @task(1)
    def check_power_state(self):
        """Запрос состояния питания"""
        self.client.get(
            "/redfish/v1/Systems/system",
            headers=self.headers,
            name="(OpenBMC) Check Power State"
        )

class PublicAPIUser(HttpUser):
  
    wait_time = between(0.5, 1.5)
    host = "https://jsonplaceholder.typicode.com"

    @task(2)
    def get_posts(self):
        """Запрос списка постов"""
        self.client.get(
            "/posts",
            name="(PublicAPI) Get Posts"
        )

    @task(1)
    def get_weather(self):
        """Запрос данных о погоде"""
        self.client.get(
            "https://wttr.in/Novosibirsk?format=j1",
            name="(PublicAPI) Get Weather"
        )
#locust -f locust_test.py
#http://localhost:8089
